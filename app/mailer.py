
from ssl import create_default_context
from email.mime.text import MIMEText
from smtplib import SMTP

def send_email(data: dict | None = None):
    msg = MailBody(**data)
    message = MIMEText(msg.body, html) 
    