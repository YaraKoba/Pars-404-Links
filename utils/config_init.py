import configparser


def load_config():
    conf = configparser.ConfigParser()
    conf.read('./config.ini')
    return conf


config = load_config()

NOTIFY = config.getboolean('Settings', 'notify', fallback=False)
NOTIFY_MAIL = config.get('Settings', 'notify_mail', fallback='')
NOTIFY_MAIL_PASSWORD = config.get('Settings', 'notify_mail_password', fallback='')

DEBUG = config.getboolean('Settings', 'debug', fallback=False)
TIMEOUT = config.get('Settings', 'timeout', fallback=10)
SITE_URL_CONFIG = config.get('input', 'site_url', fallback='')

