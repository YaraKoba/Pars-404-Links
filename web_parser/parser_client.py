import asyncio
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from utils.config_init import CHECK_EXTERNAL, TIMEOUT


def get_user_agent():
    ua = UserAgent()
    user_agent = ua.random
    header = {'User-Agent': user_agent}
    return header


class ParserClient:
    def __init__(self, url):
        self.site_url = url
        self.base_url = urlparse(url)

        self.valid_links = set()
        self.error_links = dict()
        self.timeout_err_links = dict()
        self.already_check = set()
        self.search_links = []

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

    def clear_timeout(self):
        clone_timeout = self.timeout_err_links.copy()
        for link in clone_timeout:
            if (link in self.valid_links or link in self.error_links) and link in self.timeout_err_links:
                print(f'REMOVE {link} timeout')
                self.timeout_err_links.pop(link)

    async def get_page_links(self, session, page_url):
        if page_url and page_url not in self.already_check:
            try:
                async with session.get(page_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        links = [link.get("href") for link in soup.find_all('a')]
                        self.already_check.add(page_url)
                        print(f"parser ok find {len(links)} links\n===========")
                        return links

            except aiohttp.client_exceptions.InvalidURL as err:
                print("Invalid URL:", err)
            except asyncio.TimeoutError:
                self.timeout_err_links[page_url] = {'parent': 'None', 'status_cod': 'timeout'}
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

        if link in self.valid_links or link in self.error_links:
            return

        try:
            headers = get_user_agent()
            async with session.head(link, headers=headers) as response:
                if response.status != 404:
                    if parsed_link.netloc == base_url.netloc:
                        print(f'Link {link} cod: {response.status}')
                        if link not in self.valid_links and "text/html" in response.headers.get('Content-Type'):
                            self.search_links.append(link)
                        self.valid_links.add(link)
                    else:
                        self.valid_links.add(link)
                        print(f'Link {link} cod: {response.status}')
                else:
                    print(f'Link {link} cod: {response.status}')
                    self.error_links[link] = {'parent': parent_link, 'status_cod': response.status}

        except aiohttp.client_exceptions.InvalidURL as err:
            self.error_links[link] = {'parent': parent_link, 'status_cod': err}
            print("Invalid URL:", err)
        except asyncio.TimeoutError:
            self.timeout_err_links[link] = {'parent': parent_link, 'status_cod': 'timeout'}
            print(f"Timeout Error with links {link}")
        except Exception as e:
            self.error_links[link] = {'parent': parent_link, 'status_cod': e}
            print(f"Unexpected Error with link: {link}", e)

    async def main_loop(self, session):
        while self.search_links:
            link = self.search_links.pop(0)
            print("===========\nsearch links: ", len(self.search_links))

            link = self.create_link(link)

            print("check_link: ", link)
            if link:
                new_links = await self.get_page_links(session, link)
                await asyncio.gather(
                    *[self.check_link(session, self.create_link(new_link), link)
                      for new_link in new_links])

    async def check_links_on_site(self):
        timeout = aiohttp.ClientTimeout(total=int(TIMEOUT))
        async with aiohttp.ClientSession(timeout=timeout) as session:
            self.search_links = [self.site_url]

            await self.main_loop(session)

            if self.timeout_err_links:
                print(f'START TIMEOUT {len(self.timeout_err_links)} links')
                for link in self.timeout_err_links:
                    print(f'Check timeout link {link}')
                    await self.check_link(session, link, self.timeout_err_links[link]["parent"])
                self.clear_timeout()
                print(len(self.search_links), len(self.timeout_err_links))
                await self.main_loop(session)

    async def start_parsing(self):
        await self.check_links_on_site()
        return self.valid_links, self.error_links, self.timeout_err_links
