import asyncio
from web_parser import parser_client


async def main():
    res = await parser_client.start_parsing(
        ['https://newtechaudit.ru/izvlechenie-vseh-ssylok-veb-sajta-s-pomoshhyu-python/'])
    print(res)


if __name__ == '__main__':
    asyncio.run(main())
