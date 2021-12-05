from email.message import EmailMessage
import logging
import smtplib

logger = logging.getLogger(__name__)

def connect_smtp(config):
    """Connect to an SMTP server
    Parameters:
    config  Root Config object
    """
    cfg = config.smtp

    def ssl_context():
        import ssl
        return ssl.create_default_context()

    kw = dict(host=cfg.host, port=cfg.port)
    if cfg.encryption == "ssl":
        s = smtplib.SMTP_SSL(context=ssl_context(), **kw)
    else:
        s = smtplib.SMTP(**kw)

    if cfg.encryption == "starttls":
        s.starttls(context=ssl_context())

    if cfg.username:
        s.login(cfg.username, cfg.password)

    return s


def try_send_email(config, mailto, subject, body, html=None):
    msg = EmailMessage()
    msg['From'] = config.smtp.email_from,
    msg['To'] = mailto
    msg['Subject'] = subject
    msg.set_content(body)

    if html is not None:
        msg.add_alternative(html, subtype='html')

    try:
        with connect_smtp(config) as srv:
            srv.send_message(msg)
            logger.info("Sent email to {!r}".format(msg['To']))
    except smtplib.SMTPException as e:
        logger.exception(e)
    except OSError as e:    # TimeoutError, ConnectionRefusedError
        logger.exception(e)
