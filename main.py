import asyncio
from web_parser import parser_client
from utils.config_init import DEBUG, NOTIFY, TIMEOUT, SITE_URL_CONFIG
from utils.parser_input import SITE_URL_PARSER
from utils.email_client import send_mail


async def main():
    site_url = SITE_URL_PARSER if SITE_URL_PARSER else SITE_URL_CONFIG
    print(site_url)
    valid_links, error_links, timeout_err_links = await parser_client.start_parsing(site_url, int(TIMEOUT))

    if DEBUG:
        with open('result_files/valid_links.txt', 'w') as f:
            f.write('\n'.join(valid_links))

        with open('result_files/error_links.txt', 'w') as f:
            f.write('\n'.join(error_links))

        with open('result_files/timeout_err_links.txt', 'w') as f:
            f.write('\n'.join(timeout_err_links))

    if NOTIFY and error_links:
        send_mail(text='\n'.join(error_links))

if __name__ == '__main__':
    asyncio.run(main())
