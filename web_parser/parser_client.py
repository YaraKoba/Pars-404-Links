import asyncio
from urllib.parse import urlparse
import re
import aiohttp


def create_link(link, base_url):
    if link.startswith('#') or link.startswith('mailto:') or link.startswith('tel:'):
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
                pattern = r"<a\s+(?:[^>]*?\s+)?href=[\"\']([^']*?)[\"\']"
                links = re.findall(pattern, html)
                print(f"parser ok {page_url} find {len(links)} links")
                return links

    return []


async def check_link(session, link, base_url, valid_links, error_links, timeout_err_links, search_links):
    if not link:
        return

    parsed_link = urlparse(link)
    try:
        async with session.head(link) as response:
            if response.status == 200:
                print(response.headers.get('Content-Type'))
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
        print(f"Unexpected Error with links {link}", e)


async def check_links_on_site(site_url, t):
    timeout = aiohttp.ClientTimeout(total=t)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        base_url = urlparse(site_url)
        valid_links = set()
        error_links = set()
        search_links = set()
        timeout_err_links = set()
        page_links = await get_page_links(session, site_url)
        print(page_links)
        await asyncio.gather(
            *[check_link(session, create_link(link, base_url), base_url, valid_links, error_links, timeout_err_links, search_links)
              for link in page_links])

        while search_links:
            link = search_links.pop()
            print("search links: ", len(search_links))
            print(search_links)
            print("check_link: ", link)

            link = create_link(link, base_url)
            if link:
                new_links = await get_page_links(session, link)
                await asyncio.gather(
                    *[check_link(session, create_link(new_link, base_url), base_url, valid_links, error_links, timeout_err_links, search_links)
                      for new_link in new_links if create_link(new_link, base_url) not in valid_links and create_link(new_link, base_url) not in error_links and create_link(new_link, base_url) not in timeout_err_links])

        return valid_links, error_links, timeout_err_links


async def start_parsing(url, timeout):
    site_url = url

    valid_links, error_links, timeout_err_links = await check_links_on_site(site_url, timeout)



    return valid_links, error_links, timeout_err_links
