# Parser 404 links

### Install
Clone this rep and cd in project directory
```commandline
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
Change `config.ini`

```
[Settings]
debug = 1 / 0 (result addes in file and in consol or not)
notify = 1 / 0 (send result on mail or not)
check_external = 1 / 0 (check external links or not)
timeout = sec (timeout to check links)
workers = number (number of asynchronous processes for parsing)

[input]
site_url = https://your_link_to_check.com

[Mail]
sender_mail = your mail
sender_mail_password = your mail password
receiver_email = to email
email_port = 465 (for example)
email_host = smtp.gmail.com (for example)
```

### Start parsing
If in `config.ini`
```
[input]
site_url = None
```
```commandline
python main.py https://your_link_to_check.com
```
Elif in `config.ini`
```
[input]
site_url = https://your_link_to_check.com
```
```commandline
python main.py
```

