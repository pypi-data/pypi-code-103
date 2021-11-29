#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provides SMTP mail management.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import os
import smtplib
import socket
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import time, sleep
from corut.Shell import print_error


class Smtp:
    def __init__(self):
        self.__session = None
        self.host = "smtp.gmail.com"
        self.port = 587
        self.send_as_relay_mail = False
        self.from_user = None
        self.password = None

    def login(self, timeout=60*13):
        print(f"SMTP --> Host:{self.host}/{self.port} ---> From:{self.from_user} - Relay:{self.send_as_relay_mail}")
        t = time()
        while (t + timeout) > time():
            try:
                if self.__session is None:
                    self.__session = smtplib.SMTP(self.host, self.port)
                    if not self.send_as_relay_mail:
                        context = ssl.create_default_context()
                        self.__session.ehlo()
                        self.__session.starttls(context=context)
                        self.__session.ehlo()
                        self.__session.login(self.from_user, self.password)
                    print('-------> SMTP Server Login successfully...')
                    break
            except (
                    socket.gaierror, TimeoutError, ConnectionAbortedError, ConnectionError,
                    ConnectionResetError, ConnectionRefusedError
            ) as error:
                print_error(error, locals())
                self.__session = None
                sleep(10)

    def logout(self):
        if self.__session is not None:
            self.__session.close()
        self.__session = None
        print('-------> SMTP Server Logout successfully...')

    def send_email(
            self, mail_to, mail_cc='', mail_bcc='', subject='', details='', attachment_path=None,
            embedded_image_status=True
    ):
        """

        :param mail_to: Mailing list to be seen in To
        :param mail_cc: Mailing list to be seen in CC
        :param mail_bcc: Mailing list to be seen in BCC
        :param subject: Text to be seen in the subject title
        :param details: Text in the post
        :param attachment_path: File path list if you want to add files. if it is singular, it can also be a string.
        :param embedded_image_status: Option to send as embedded if there are png, bmp, jpg in the files sent.
        """
        print(f'Mail TO:{mail_to}', f'Mail CC:{mail_cc}', f'Mail BCC:{mail_bcc}')
        print(f'Mail Subject:{subject}')
        print(f'Mail Details:{details}')
        print(f'Mail Attachment Paths:{attachment_path}', f'Mail Embeded Image Status:{embedded_image_status}')
        msg = MIMEMultipart('related')
        try:
            msg['From'] = self.from_user
            msg['To'] = mail_to
            msg['Cc'] = mail_cc
            msg['Subject'] = subject
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
            msg_alternative.attach(MIMEText(details, 'plain'))
            html_file_link = ''
            for line in details.split('\n'):
                html_file_link += f'<br>{line}\n'
            html_file_link += '<br><br/>'
            if attachment_path is not None:
                for file_path in (attachment_path if isinstance(attachment_path, list) else [attachment_path]):
                    try:
                        filename = os.path.basename(file_path)
                        with open(file_path, 'rb') as f:
                            attachment = f.read()
                    except Exception as error:
                        attachment = None
                        print(f"#######> Send Email Attachment File Error:{error}###")
                        filename = None
                    if attachment is not None:
                        if (
                                embedded_image_status and
                                filename is not None and
                                str(filename).lower().split('.')[1] in ('jpg', 'png', 'bmp')
                        ):
                            html_file_link += f'<img src="cid:{filename}"><p>{filename}</p>'
                            msg_image = MIMEImage(attachment)
                            msg_image.add_header('Content-ID', filename)
                            msg_image.add_header('X-Attachment-Id', filename)
                            msg_image['Content-Disposition'] = f'inline; filename={filename}'
                            msg.attach(msg_image)
                        else:
                            p = MIMEBase('application', 'octet-stream')
                            p.set_payload(attachment)
                            encoders.encode_base64(p)
                            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
                            msg.attach(p)
                    print(f'{file_path} file was attached to the mail...')
                msg_alternative.attach(MIMEText(html_file_link, 'html'))
            if self.__session is None:
                self.login()
            self.__session.sendmail(
                self.from_user,
                msg['To'].split(';') + msg['Cc'].split(';') + mail_bcc.split(';'),
                msg.as_string()
            )
            print('-------> Post sent successfully...')
        except Exception as error:
            print_error(error, locals())
            self.logout()
