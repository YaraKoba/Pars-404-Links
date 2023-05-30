import asyncio
from bs4 import BeautifulSoup
from utils.aiohttp_client import _get, check_link


async def get_all_url_page(urls):
    list_urls = []
    responses = await asyncio.gather(*(_get(url) for url in urls))
    for resp in responses:
        soup = BeautifulSoup(resp, 'html.parser')
        list_urls.append([a['href'] for a in soup.find_all('a', href=True)])
    result = {t: r for (t, r) in zip(urls, list_urls)}
    return result


async def check_url(urls):
    links_404 = []
    for url in urls:
        status = await check_link(url)
        if status == '404':
            links_404.append(url)
    return links_404


async def start_parsing(url):
    urls = await get_all_url_page(url)
    res = []
    for url in urls:
        check_404 = await check_url(urls[url])
        res.append(check_404)
    return res
