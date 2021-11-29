from .config import GMAIL_SMTP_SERVER, GMAIL_IMAP_SERVER
from .mailer import Mailer


class GmailMailer(Mailer):
    """
    Gmail mail sender library
    """
    smtp_server = GMAIL_SMTP_SERVER
    imap_server = GMAIL_IMAP_SERVER
