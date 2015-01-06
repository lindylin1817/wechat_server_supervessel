#!/usr/bin/env python
#encoding:utf-8

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from email.utils import COMMASPACE, formatdate
from email import encoders

import smtplib

import os

def send_mail(smtp_server, mail_user, mail_passwd, fro, to, subject, text, files=[]):
    assert type(to) == list
    assert type(files) == list

    msg = MIMEMultipart()
    msg['From'] = fro
    msg['Subject'] = subject
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime = True)
    msg.attach(MIMEText(text, _charset='utf-8'))

    for file in files:
	part = MIMEBase('application', 'octet-stream')
	part.set_payload(open(file, 'rb').read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
	msg.attach(part)

    smtp = smtplib.SMTP(smtp_server)
    smtp.login(mail_user, mail_passwd)
    smtp.sendmail(fro, to, msg.as_string())
    smtp.close()
	
