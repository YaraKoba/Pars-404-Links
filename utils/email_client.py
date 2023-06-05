from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl

from utils.config_init import SENDER_MAIL, SENDER_MAIL_PASSWORD, RECEIVER_MAIL, EMAIL_HOST, EMAIL_PORT


def send_mail(text):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    context.set_ciphers('HIGH:!DH:!aNULL')

    subject = 'Broken links found on website'
    message = 'The following links returned a 404 status code:\n\n'
    message += text

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = SENDER_MAIL
    msg['To'] = RECEIVER_MAIL

    msg.attach(MIMEText(message, 'html'))
    try:
        # Establish a secure connection with the SMTP server
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            # Login to the SMTP server
            server.login(SENDER_MAIL, SENDER_MAIL_PASSWORD)

            # Send the email
            print(server.send_message(msg))
        print(f"Email sent successfully to {RECEIVER_MAIL}!")
    except smtplib.SMTPException as e:
        print("Failed to send email. Error:", str(e))
