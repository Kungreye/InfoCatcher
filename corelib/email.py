# _*_ coding: utf-8 _*_

import smtplib

from flask_mail import sanitize_addresses

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD


def send_mail_task(msg):
    send_to = list(sanitize_addresses(msg.send_to))
    part = MIMEText(_text=msg.html, _subtype='html')

    mp = MIMEMultipart('alternative')
    mp['Subject'] = msg.subject
    mp['From'] = 'no-reply@InfoCatcher.com'
    mp['To'] = ','.join(send_to)
    mp.attach(part)

    s = smtplib.SMTP_SSL(host=MAIL_SERVER, port=MAIL_PORT)
    s.login(MAIL_USERNAME, MAIL_PASSWORD)
    s.sendmail(from_addr=MAIL_USERNAME, to_addrs=send_to, msg=bytes(mp.as_string(), 'utf-8'))
    s.quit()
