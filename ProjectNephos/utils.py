from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP


def send_mail(subject, body, config):
    Message = MIMEMultipart()

    Message["Subject"] = subject
    Message["From"] = config["mail", "From"]
    Message["To"] = config["mail", "admin"]
    Message.attach(MIMEText(body, "plain"))

    host = config["mail", "host"]
    port = int(config["mail", "port"])
    server = SMTP(host, port)

    server.send_message(Message)
