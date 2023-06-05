import aiohttp
import asyncio


async def _get(url, param=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=param) as resp:
            return await resp.text()


async def check_link(url):
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as resp:
            print(resp.status)
            return resp.status
