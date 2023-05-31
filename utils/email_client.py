from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl


def send_mail(sender_mail, sender_password, receiver_email, text):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    context.set_ciphers('HIGH:!DH:!aNULL')

    subject = 'Broken links found on website'
    message = 'The following links returned a 404 status code:\n\n'
    message += text

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_mail
    msg['To'] = receiver_email

    msg.attach(MIMEText(message, 'plain'))
    try:
        # Establish a secure connection with the SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            # Login to the SMTP server
            server.login(sender_mail, sender_password)

            # Send the email
            server.send_message(msg)
        print(f"Email sent successfully to {receiver_email}!")
    except smtplib.SMTPException as e:
        print("Failed to send email. Error:", str(e))
