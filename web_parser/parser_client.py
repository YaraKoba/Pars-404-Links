import asyncio
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

from utils.config_init import CHECK_EXTERNAL, TIMEOUT


def create_link(link, base_url):
    if not link:
        return

    if not link or link.startswith('#')\
            or link.startswith('mailto:') \
            or link.startswith('tel:') \
            or link.startswith('skype:') \
            or link.startswith('javascript:'):
        return

    parsed_link = urlparse(link)
    if not parsed_link.netloc:
        link = base_url.scheme + '://' + base_url.netloc + link
        return link
    else:
        return link


async def get_page_links(session, page_url):
    if page_url:
        async with session.get(page_url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                links = [link.get("href") for link in soup.find_all('a')]
                print(f"parser ok {page_url} find {len(links)} links")
                return links

    return []


async def check_link(session, link, base_url, valid_links, error_links, timeout_err_links, search_links, parent_link):
    parsed_link = urlparse(link)
    if not CHECK_EXTERNAL and parsed_link.netloc != base_url.netloc:
        return

    if not link or link in valid_links or link in error_links or link in timeout_err_links:
        return

    try:
        async with session.head(link) as response:
            if response.status == 200:
                if parsed_link.netloc == base_url.netloc:
                    print(f'Link {link} cod: {response.status}')
                    if link not in valid_links and response.headers.get('Content-Type') == "text/html; charset=UTF-8":
                        search_links.add(link)
                    valid_links.add(link)
                else:
                    valid_links.add(link)
                    print(f'Link {link} cod: {response.status}')
            elif response.status == 404:
                print(f'Link {link} cod: {response.status}')
                error_links[link] = {'parent': parent_link, 'status_cod': response.status}

    except aiohttp.client_exceptions.InvalidURL as err:
        error_links[link] = {'parent': parent_link, 'status_cod': response.status}
        print("Invalid URL:", err)
    except asyncio.TimeoutError:
        timeout_err_links.add(link)
        print(f"Timeout Error with links {link}")
    except Exception as e:
        print(f"Unexpected Error with link: {link}", e)


async def check_links_on_site(site_url):
    timeout = aiohttp.ClientTimeout(total=int(TIMEOUT))
    async with aiohttp.ClientSession(timeout=timeout) as session:
        base_url = urlparse(site_url)
        valid_links = set()
        error_links = dict()
        timeout_err_links = set()

        search_links = set()

        page_links = await get_page_links(session, site_url)
        print(page_links)
        await asyncio.gather(
            *[check_link(session,
                         create_link(link, base_url),
                         base_url,
                         valid_links,
                         error_links,
                         timeout_err_links,
                         search_links,
                         site_url)
              for link in page_links])

        while search_links:
            link = search_links.pop()
            print("search links: ", len(search_links))
            print("check_link: ", link)
            link = create_link(link, base_url)
            if link:
                new_links = await get_page_links(session, link)
                await asyncio.gather(
                    *[check_link(session, create_link(new_link, base_url), base_url, valid_links, error_links,
                                 timeout_err_links, search_links, link)
                      for new_link in new_links])

        return valid_links, error_links, timeout_err_links


async def start_parsing(url):
    site_url = url
    valid_links, error_links, timeout_err_links = await check_links_on_site(site_url)

    return valid_links, error_links, timeout_err_links
