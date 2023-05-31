# Parser 404 links

### Install
Clone this rep and cd in project directory
```commandline
virtualenv venv
source /usr/local/www/www9/para_kzn_bot/venv/bin/activate
pip install -r requirements.txt
```
Change `config.ini`

```
[Settings]
debug = 1 / 0 (result addes in file or not)
notify = 1 / 0 (send result on mail or not)
timeout = sec (timeout to check links)

[input]
site_url = https://your_link_to_check.com

[Mail]
sender_mail = your mail
sender_mail_password = your mail password
receiver_email = to email
```

### Start paesing
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