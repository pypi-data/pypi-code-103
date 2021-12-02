# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Union

import textwrap

from flask import current_app, render_template, has_app_context
from flask_mail import Message

from .. import create_app
from ..models import User

str_or_list = Union[str, List[str]]


def send_email(subject: str, body: str, sender: str_or_list = None, recipient: str_or_list = None):
    # Make sure there is a app context
    context = None
    if not has_app_context():
        app = create_app()
        context = app.app_context()
        context.push()

    prefix = current_app.config['PIDB_EMAIL_PREFIX']

    if sender is None:
        sender = current_app.config['PIDB_EMAIL_FROM']

    if recipient is None:
        recipient = current_app.config['PIDB_EMAIL_TO']

    # The recipient always has to be a list
    if isinstance(recipient, str):
        recipient = recipient.split(',')

    if not isinstance(recipient, list):
        recipient = list(recipient)

    body = textwrap.dedent(body).strip()
    html = render_template('generic_email.html', message=body)

    message = Message(
        subject='{prefix} {subject}'.format(prefix=prefix, subject=subject),
        recipients=recipient,
        body=body,
        html=html,
    )

    if sender:
        message.sender = sender

    mail = current_app.extensions.get("mail")
    mail.send(message)

    if context is not None:
        context.pop()

    return """Email send succesfully: 
FROM: {sender},
TO: {to},
SUBJECT: {subject},
BODY:\n{body}""".format(sender=sender, to=recipient, subject=subject, body=body)


def send_bulk_mail(recipients: List[User], subject: str, body: str):
    # Make sure there is a app context
    context = None
    if not has_app_context():
        app = create_app()
        context = app.app_context()
        context.push()

    mail = current_app.extensions.get("mail")
    prefix = current_app.config['PIDB_EMAIL_PREFIX']

    with mail.connect() as connection:
        for user in recipients:
            body_rendered = body.format(user=user)
            html = render_template('generic_email.html', message=body_rendered)
            subject_rendered = f"{prefix} {subject.format(user=user)}"
            message = Message(recipients=[user.email],
                              body=body_rendered,
                              html=html,
                              subject=subject_rendered)
            message.sender = current_app.config['PIDB_EMAIL_FROM']
            connection.send(message)

    if context is not None:
        context.pop()
