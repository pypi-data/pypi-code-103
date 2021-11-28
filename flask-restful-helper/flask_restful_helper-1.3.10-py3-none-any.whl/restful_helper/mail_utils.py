from flask_mail import Message
from app.extensions import mail, celery
from app.extensions import create_app
import os


@celery.task()
def send_email(subject, recipients: list, cc: list = None, body=None, html=None, attachments=None):
    config_type = os.getenv('CONFIG_TYPE', 'dev')
    app = create_app(config_type=config_type)
    with app.app_context():
        with mail.connect() as conn:
            msg = Message(
                subject=subject,
                body=body,
                html=html,
                attachments=attachments,
                cc=cc,
                recipients=recipients
            )
            return conn.send(msg)
