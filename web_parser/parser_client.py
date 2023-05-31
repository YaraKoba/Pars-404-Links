import asyncio
from urllib.parse import urlparse
import re
import aiohttp
from bs4 import BeautifulSoup

from utils.config_init import CHECK_EXTERNAL


def create_link(link, base_url):
    if not link:
        return
    if not link or link.startswith('#') or link.startswith('mailto:') or link.startswith('tel:') or link.startswith('skype:'):
        return

    parsed_link = urlparse(link)
    if not parsed_link.netloc:
        link = base_url.scheme + '://' + base_url.netloc + link
        return link
    else:
        return link


def clear_search(links: set, already_links: set):
    for link in links:
        if link in already_links:
            print(f'REPEAT!!! link {link} is REPEAT!!!')


async def get_page_links(session, page_url, already_check):
    if page_url:
        async with session.get(page_url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                links = [link.get("href") for link in soup.find_all('a')]
                print(f"parser ok {page_url} find {len(links)} links")
                already_check.add(page_url)
                return links

    return []


async def check_link(session, link, base_url, valid_links, error_links, timeout_err_links, search_links, already_check):
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
                error_links.add(link)

    except aiohttp.client_exceptions.InvalidURL as err:
        error_links.add(link)
        print("Invalid URL:", err)
    except asyncio.TimeoutError:
        timeout_err_links.add(link)
        print(f"Timeout Error with links {link}")
    except Exception as e:
        print(f"Unexpected Error with link: {link}", e)


async def check_links_on_site(site_url, t):
    timeout = aiohttp.ClientTimeout(total=t)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        base_url = urlparse(site_url)
        valid_links = set()
        error_links = set()
        timeout_err_links = set()

        search_links = set()
        already_check = set()

        page_links = await get_page_links(session, site_url, already_check)
        print(page_links)
        await asyncio.gather(
            *[check_link(session,
                         create_link(link, base_url),
                         base_url,
                         valid_links,
                         error_links,
                         timeout_err_links,
                         search_links,
                         already_check)
              for link in page_links])

        while search_links:
            link = search_links.pop()
            print("search links: ", len(search_links))
            print("check_link: ", link)
            clear_search(search_links, already_check)
            link = create_link(link, base_url)
            if link:
                new_links = await get_page_links(session, link, already_check)
                await asyncio.gather(
                    *[check_link(session, create_link(new_link, base_url), base_url, valid_links, error_links,
                                 timeout_err_links, search_links, already_check)
                      for new_link in new_links])

        return valid_links, error_links, timeout_err_links


async def start_parsing(url, timeout):
    site_url = url
    valid_links, error_links, timeout_err_links = await check_links_on_site(site_url, timeout)

    return valid_links, error_links, timeout_err_links
