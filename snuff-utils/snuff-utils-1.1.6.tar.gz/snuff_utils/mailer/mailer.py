#!/usr/bin/env python2.7
# coding=utf-8

from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itertools import islice
from os.path import basename
from smtplib import SMTP_SSL

from imbox import Imbox

from snuff_utils.DottedDict import DottedDict
from .config import YANDEX_SMTP_SERVER
from snuff_utils.decorators import as_list


class Mailer():
    """
    Класс, реализующий библиотеку для отправки электронной почты с помощью яндекс
    """

    smtp_server = YANDEX_SMTP_SERVER
    email = None
    password = None

    def __init__(self, email=None, password=None):
        self.__class__.email = email
        self.__class__.password = password
        super().__init__()

    @classmethod
    def send_mail(cls, recipients_emails, title, sender_email=None, password=None, body=None, attachment=None):
        sender_email, password = cls.define_access_variables(sender_email, password)
        # Преобразуем recipients_emails к списку
        recipients_emails = recipients_emails.split(',') \
            if isinstance(recipients_emails, str) else recipients_emails

        # Формируем сообщение
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ','.join(recipients_emails)
        msg['Subject'] = title
        if body and isinstance(body, MIMEText):
            msg.attach(body)
        elif body:
            msg.attach(cls.form_text_body(body))
        if attachment:
            msg.attach(attachment)

        # Отправка
        smtp = SMTP_SSL(cls.smtp_server)
        smtp.connect(cls.smtp_server)
        smtp.login(sender_email, password)
        smtp.sendmail(sender_email, recipients_emails, msg.as_string())
        smtp.quit()

    @staticmethod
    def form_html_body(html):
        return MIMEText(html, 'html')

    @staticmethod
    def form_text_body(text):
        return MIMEText(text, 'plain')

    @staticmethod
    def form_attachment(filename, name=''):
        if not name:
            name = basename(filename)
        # Формируем вложение
        attachment = MIMEBase('application', "octet-stream")
        attachment.set_payload(open(filename, "rb").read())
        encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=name)
        return attachment

    @classmethod
    @as_list
    def iter_inbox(cls, email=None, password=None, offset=0, limit=0, unread=False, folder=None,
                   sent_from=None, sent_to=None, date=None, date_from=None, date_until=None,
                   mark_as_read=False, move_to_folder=None, **filters):
        def paginate(messages, offset, limit):
            paginate = None
            if offset and limit:
                paginate = (offset, offset + limit)
            elif offset:
                paginate = (offset, None)
            elif limit:
                paginate = [limit]
            if paginate:
                return islice(messages, *paginate)
            return messages
        email, password = cls.define_access_variables(email, password)
        # Prepare filters
        if unread:
            filters['unread'] = unread
        if folder:
            filters['folder'] = folder
        if sent_from:
            filters['sent_from'] = sent_from
        if sent_to:
            filters['sent_to'] = sent_to
        if date:
            filters['date__on'] = date
        if date_from:
            filters['date__gt'] = date_from
        if date_until:
            filters['date__lt'] = date_until

        with Imbox(cls.imap_server,
                   username=email,
                   password=password,
                   ssl=True,
                   ssl_context=None,
                   starttls=False) as imbox:
            # Filtering
            messages = imbox.messages(**filters)
            # Pagination
            messages = paginate(messages, offset, limit)
            # Iterate
            for uid, message in messages:
                if mark_as_read:
                    imbox.mark_seen(uid)
                if move_to_folder:
                    imbox.move(uid=uid, destination_folder=move_to_folder)
                yield DottedDict({
                    'id': uid,
                    'from': [DottedDict(i) for i in message.sent_from],
                    'to': [DottedDict(i) for i in message.sent_to],
                    'date': message.parsed_date,
                    'subject': message.subject,
                    'body': DottedDict(message.body),
                })

    @classmethod
    def define_access_variables(cls, email, password):
        if not email:
            email = cls.email
        if not email:
            raise ValueError('No email specified.')
        if not password:
            password = cls.password
        if not password:
            raise ValueError('No email specified.')
        return email, password

    @classmethod
    def mark_as_read(cls, uid, email=None, password=None):
        email, password = cls.define_access_variables(email, password)
        with Imbox(cls.imap_server,
                   username=email,
                   password=password,
                   ssl=True,
                   ssl_context=None,
                   starttls=False) as imbox:
            imbox.mark_seen(uid)

    @classmethod
    def move_to_folder(cls, uid, folder, email=None, password=None):
        email, password = cls.define_access_variables(email, password)
        with Imbox(cls.imap_server,
                   username=email,
                   password=password,
                   ssl=True,
                   ssl_context=None,
                   starttls=False) as imbox:
            imbox.move(uid=uid, destination_folder=folder)
