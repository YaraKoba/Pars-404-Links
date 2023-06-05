import asyncio
from web_parser.parser_client import ParserClient
from utils.config_init import DEBUG, NOTIFY, SITE_URL_CONFIG
from utils.parser_input import SITE_URL_PARSER
from utils.email_client import send_mail
from utils.create_message import create_pandas, create_html_template
from datetime import datetime


async def main():
    site_url = SITE_URL_PARSER if SITE_URL_PARSER else SITE_URL_CONFIG
    print('start check for', site_url)
    parser = ParserClient(site_url)

    start = datetime.now()
    valid_links, error_links, timeout_err_links = await parser.start_parsing()
    end = datetime.now()
    time = end - start


    if DEBUG:
        message_err = create_pandas(error_links)
        message_time = create_pandas(timeout_err_links)

        with open('result_files/valid_links.txt', 'w') as f:
            f.write('\n'.join(valid_links))

        with open('result_files/error_links.txt', 'w') as f:
            if error_links:
                print('\nERROR links:')
                print(message_err)
            f.write(str(message_err))

        with open('result_files/timeout_err_links.txt', 'w') as f:
            if timeout_err_links:
                print("\nTimeERROR links:")
                print(message_time)
            f.write('\n'.join(message_time))

    if NOTIFY and error_links:
        message = create_html_template(error_links)
        send_mail(text=message)

    v, e, t = len(valid_links), len(error_links), len(timeout_err_links)
    print(f'\nParser end successful time - "{str(time)[2:][:-7]}"\n'
          f'links: {v+e+t}\n'
          f'Valid links: {v}\n'
          f'Error links: {e}\n'
          f'Timeout links: {t}')

if __name__ == '__main__':
    asyncio.run(main())
