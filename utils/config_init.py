import configparser


def load_config():
    conf = configparser.ConfigParser()
    conf.read('./config.ini')
    return conf


config = load_config()

NOTIFY = config.getboolean('Settings', 'notify', fallback=False)
DEBUG = config.getboolean('Settings', 'debug', fallback=False)
TIMEOUT = int(config.get('Settings', 'timeout', fallback=10))
CHECK_EXTERNAL = config.getboolean('Settings', 'check_external', fallback=True)
WORKERS = int(config.get('Settings', 'workers', fallback=10))

SITE_URL_CONFIG = config.get('input', 'site_url', fallback='')

SENDER_MAIL = config.get('Mail', 'sender_mail', fallback='')
SENDER_MAIL_PASSWORD = config.get('Mail', 'sender_mail_password', fallback='')
RECEIVER_MAIL = config.get('Mail', 'receiver_email', fallback='')
EMAIL_PORT = config.get('Mail', 'email_port', fallback='')
EMAIL_HOST = config.get('Mail', 'email_host', fallback='')






