import argparse
from utils.config_init import SITE_URL_CONFIG

def parse_arguments():
    if not SITE_URL_CONFIG:
        parser = argparse.ArgumentParser(description='Website link checker script')
        parser.add_argument('site_url', help='Website URL')
        return parser.parse_args()
    return None


args = parse_arguments()
SITE_URL_PARSER = None if not args else args.site_url
