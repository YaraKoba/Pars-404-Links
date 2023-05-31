from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl


def send_mail(mail, password, text):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    context.set_ciphers('HIGH:!DH:!aNULL')

    subject = 'Broken links found on website'
    message = 'The following links returned a 404 status code:\n\n'
    message += text

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = mail
    msg['To'] = mail

    msg.attach(MIMEText(message, 'plain'))
    try:
        # Establish a secure connection with the SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 587) as server:
            # Login to the SMTP server
            server.login(mail, password)

            # Send the email
            server.send_message(msg)
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print("Failed to send email. Error:", str(e))
