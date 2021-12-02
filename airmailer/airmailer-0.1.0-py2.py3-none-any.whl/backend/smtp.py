#!/usr/bin/env python
# -*- coding: utf-8 -*-
import smtplib
import socket
import ssl
import threading

from ..message import sanitize_address
from .base import BaseEmailBackend


class SMTPEmailBackend(BaseEmailBackend):
    """
    A wrapper that manages the SMTP network connection.
    """
    def __init__(self, host, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None,
                 **kwargs):
        """Creates a client for the an SMTP server.

        :param host: the hostname or IP address of the SMTP server
        :type host: str

        :param port: the port for the SMTP server, defaults to None
        :type port: str, optional

        :param username: the username to use to authenticate to the SMTP server, defaults to None
        :type username: str, optional

        :param password: the password to use to authenticate to the SMTP server, defaults to None
        :type password: str, optional

        :param use_tls: If `True`, issue StartTLS on the SMTP connection.  Mutually exclusive with
            ``use_ssl``, defaults to False
        :type password: bool, optional

        :param fail_silently: If `True`, don't raise execeptions on client errors, defaults to False
        :type fail_silently: bool

        :param use_ssl: If `True`, use SSL to connect to the SMTP server.  Mutually exclusive with
            ``use_tls``, defaults to False
        :type use_ssl: bool, optional

        :param timeout: Timeout for the TCP connection to the SMTP server in seconds, defaults to `None`
        :type timeout: int, optional

        :param ssl_keyfile: client SSL key file contents, defaults to `None`
        :type ssl_keyfile: str, optional

        :param ssl_certfile: client SSL cert file contents, defaults to `None`
        :type ssl_certfile: str, optional
        """
        super().__init__(fail_silently=fail_silently)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.ssl_keyfile = ssl_keyfile
        self.ssl_certfile = ssl_certfile
        if self.use_ssl and self.use_tls:
            raise ValueError(
                "EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive, so only set "
                "one of those settings to True.")
        self.connection = None
        self._lock = threading.RLock()

    @property
    def connection_class(self):
        return smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP

    def open(self):
        """
        Open a connection to the email server.

        :return: Return `True` if a new connection was required, `False` if not,
            `None` if we had an exception and `fail_silently` is `True`
        :rtype: bool or None
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False

        # If local_hostname is not specified, socket.getfqdn() gets used.
        # For performance, we use the cached FQDN for local_hostname.
        connection_params = {'local_hostname': socket.getfqdn()}
        if self.timeout is not None:
            connection_params['timeout'] = self.timeout
        if self.use_ssl:
            connection_params.update({
                'keyfile': self.ssl_keyfile,
                'certfile': self.ssl_certfile,
            })
        try:
            self.connection = self.connection_class(self.host, self.port, **connection_params)

            # TLS/SSL are mutually exclusive, so only attempt TLS over
            # non-secure connections.
            if not self.use_ssl and self.use_tls:
                self.connection.starttls(keyfile=self.ssl_keyfile, certfile=self.ssl_certfile)
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise

    def close(self):
        """Close the connection to the email server."""
        if self.connection is None:
            return
        try:
            try:
                self.connection.quit()
            except (ssl.SSLError, smtplib.SMTPServerDisconnected):
                # This happens when calling quit() on a TLS connection
                # sometimes, or when the connection was already disconnected
                # by the server.
                self.connection.close()
            except smtplib.SMTPException:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    def send_messages(self, email_messages):
        """
        Sends one or more messages returns the number of email messages sent.

        :param email_messages: A list of emails to send
        :type email_messages: List[airmailer.message.EmailMessage]

        :return: count of messages sent
        :rtype: int
        """
        if not email_messages:
            return 0
        with self._lock:
            new_conn_created = self.open()
            if not self.connection or new_conn_created is None:
                # We failed silently on open().
                # Trying to send would be pointless.
                return 0
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            if new_conn_created:
                self.close()
        return num_sent

    def _send(self, email_message):
        """
        Sends an individual message.

        :param email_message: An email to send
        :type email_message: class:`airmailer.message.EmailMessage`

        :return: `True` if the message was sent, `False otherwise
        :rtype: bool
        """

        if not email_message.recipients():
            return False
        encoding = email_message.encoding
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        message = email_message.message()
        try:
            self.connection.sendmail(from_email, recipients, message.as_bytes(linesep='\r\n'))
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise
            return False
        return True
