import asyncio
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from utils.config_init import CHECK_EXTERNAL, TIMEOUT, WORKERS


def get_user_agent():
    ua = UserAgent()
    user_agent = ua.random
    header = {'User-Agent': user_agent}
    return header


class ParserClient:
    def __init__(self, url):
        self.site_url = url
        self.base_url = urlparse(url)

        self.q = asyncio.Queue()

        self.valid_links = set()
        self.error_404 = dict()
        self.any_error = dict()
        self.timeout_err_links = dict()
        self.already_check = set()

    def create_link(self, link):
        base_url = self.base_url
        if not link or any(link.startswith(prefix) for prefix in ['#', 'mailto:', 'tel:', 'skype:', 'javascript:']):
            return

        parsed_link = urlparse(link)
        if not parsed_link.scheme:
            link = parsed_link._replace(scheme=base_url.scheme, netloc=base_url.netloc).geturl()
            return link
        else:
            return link

    def clear_timeout_anyerr(self):
        clone_timeout = self.timeout_err_links.copy()
        clone_any_err = self.any_error.copy()
        for link in clone_timeout:
            if (link in self.valid_links or link in self.error_404) and link in self.timeout_err_links:
                print(f'REMOVE {link} timeout')
                self.timeout_err_links.pop(link)

        for link in clone_any_err:
            if (link in self.valid_links or link in self.error_404) and link in self.any_error:
                print(f'REMOVE {link} timeout')
                self.any_error.pop(link)

    async def clean_err(self, session):
        if self.timeout_err_links:
            print(f'START TIMEOUT clean {len(self.timeout_err_links)} links')
            await asyncio.gather(*(self.check_link(session, link, self.timeout_err_links[link]["parent"])
                                   for link in self.timeout_err_links))
        if self.any_error:
            print(f'START Error clean {len(self.any_error)} links')
            await asyncio.gather(*(self.check_link(session, link, self.any_error[link]["parent"])
                                   for link in self.any_error))
        self.clear_timeout_anyerr()
        print(self.q.qsize(), len(self.timeout_err_links))
        if self.q.qsize():
            await self.check_links_on_site()

    async def get_page_links(self, session, page_url):
        if page_url and page_url not in self.already_check:
            try:
                async with session.get(page_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        links = [link.get("href") for link in soup.find_all('a')]
                        self.already_check.add(page_url)
                        return links

            except aiohttp.client_exceptions.InvalidURL as err:
                print("Invalid URL:", err)
            except asyncio.TimeoutError:
                self.timeout_err_links[page_url] = {'parent': 'None', 'status_code': 'timeout'}
                print(f"Timeout Error with links {page_url}")
            except Exception as err:
                print(f"Unexpected Error in get with link: {page_url}", err)

        return []

    async def check_link(self, session, link, parent_link):
        parsed_link = urlparse(link)
        base_url = self.base_url

        if not link:
            return

        if not CHECK_EXTERNAL and parsed_link.netloc != base_url.netloc:
            print(f'Link {link} is external, change config')
            return

        if link in self.valid_links:
            return

        try:
            headers = get_user_agent()
            async with session.head(link, headers=headers) as response:
                if response.status != 404:
                    if parsed_link.netloc == base_url.netloc:
                        print(f'Link {link} code: {response.status}')
                        if link not in self.valid_links and "text/html" in response.headers.get('Content-Type'):
                            await self.q.put(link)
                        self.valid_links.add(link)
                    else:
                        self.valid_links.add(link)
                        print(f'Link {link} code: {response.status}')
                else:
                    print(f'Link {link} code: {response.status}')
                    self.error_404[link] = {'parent': parent_link, 'status_code': response.status}

        except aiohttp.client_exceptions.InvalidURL as err:
            self.error_404[link] = {'parent': parent_link, 'status_code': err}
            print("Invalid URL:", err)
        except asyncio.TimeoutError:
            self.timeout_err_links[link] = {'parent': parent_link, 'status_code': 'timeout'}
            print(f"Timeout Error with links {link}")
        except Exception as e:
            self.any_error[link] = {'parent': parent_link, 'status_code': e}
            print(f"Unexpected Error with link: {link}", e)

    async def main_loop(self, session):
        while True:
            link = await self.q.get()
            link = self.create_link(link)
            print(f'Size q: {self.q.qsize()}')
            if link:
                new_links = await self.get_page_links(session, link)
                await asyncio.gather(
                    *[self.check_link(session, self.create_link(new_link), link)
                      for new_link in new_links])

            self.q.task_done()

    async def check_links_on_site(self):
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            await self.q.put(self.site_url)

            tasks = []
            for _ in range(WORKERS):
                task = asyncio.create_task(self.main_loop(session))
                tasks.append(task)

            await self.q.join()

            for task in tasks:
                task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)

            await self.clean_err(session)

    async def start_parsing(self):
        await self.check_links_on_site()
        return self.valid_links, self.error_404, self.timeout_err_links, self.any_error
