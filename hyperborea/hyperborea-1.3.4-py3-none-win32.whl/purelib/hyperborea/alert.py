import collections
import datetime
import email.message
import email.utils
import logging
import smtplib
import time
import threading

from PySide2 import QtCore

logger = logging.getLogger(__name__)


Alert = collections.namedtuple(
    "Alert", ['subchannel_name', 'alert_type', 'limit', 'value'])


def validate_email_settings(email_settings):
    email_settings = email_settings.copy()

    s_keys = ['from_address', 'to_address', 'smtp_host', 'smtp_user',
              'smtp_password']

    for s in s_keys:
        if s not in email_settings or email_settings[s] is None:
            email_settings[s] = ''
        else:
            email_settings[s] = email_settings[s].strip()

    if ('smtp_port' not in email_settings or
            email_settings['smtp_port'] is None):
        email_settings['smtp_port'] = 587

    if ('use_auth' not in email_settings or
            email_settings['use_auth'] is None):
        email_settings['use_auth'] = True

    if 'security' not in email_settings:
        email_settings['security'] = 'starttls'
    else:
        security = email_settings['security']
        if security is None:
            email_settings['security'] = 'starttls'
        elif security not in ['', 'starttls', 'ssl']:
            raise ValueError('unknown security setting')

    if email_settings['from_address'] == '':
        raise ValueError('no email from address')

    if email_settings['to_address'] == '':
        raise ValueError('no email to address')

    return email_settings


def _get_smtp_object(email_settings):
    security = email_settings['security']
    if security == 'ssl':
        smtp_obj = smtplib.SMTP_SSL(host=email_settings['smtp_host'],
                                    port=email_settings['smtp_port'])
    else:
        smtp_obj = smtplib.SMTP(host=email_settings['smtp_host'],
                                port=email_settings['smtp_port'])

    if security == 'starttls':
        smtp_obj.starttls()

    if email_settings['use_auth']:
        smtp_obj.login(user=email_settings['smtp_user'],
                       password=email_settings['smtp_password'])

    return smtp_obj


def send_test_email(email_settings):
    email_settings = validate_email_settings(email_settings)

    msg = email.message.EmailMessage()
    msg['From'] = email_settings['from_address']
    msg['To'] = email_settings['to_address']
    msg['Subject'] = 'Alert test email'
    msg['Date'] = email.utils.formatdate()
    msg['Message-ID'] = email.utils.make_msgid()

    body = "This is an email sent to test the alert email configuration."
    msg.set_content(body)

    smtp_obj = _get_smtp_object(email_settings)
    try:
        smtp_obj.send_message(msg)
    finally:
        smtp_obj.quit()


class AlertManager(QtCore.QObject):
    def __init__(self, email_settings):
        super().__init__()

        self.last_sent = {}  # k: serial_number, v: datetime

        self.email_settings = validate_email_settings(email_settings)

        self.is_finished = threading.Event()
        self.alerts = collections.deque()
        self.email_thread = threading.Thread(target=self._email_loop)

        # start
        self.email_thread.start()

    def _create_message(self, alert_tuple):
        serial_number, display_name, alert_list, dt = alert_tuple

        if display_name == serial_number:
            name = serial_number
        else:
            name = "{} ({})".format(display_name, serial_number)

        msg = email.message.EmailMessage()
        msg['From'] = self.email_settings['from_address']
        msg['To'] = self.email_settings['to_address']
        msg['Subject'] = '[{}] Alert'.format(name)
        msg['Date'] = email.utils.format_datetime(dt)
        msg['Message-ID'] = email.utils.make_msgid()

        timestr = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        lines = [(f"{name} experienced an alert condition at {timestr}"
                  " with the following:"),
                 ""]

        for a in alert_list:
            alert_type = a.alert_type.capitalize()
            s = (f'{alert_type} alert triggered on "{a.subchannel_name}",'
                 f' value {a.value} is outside limit of {a.limit}.')
            lines.append(s)

        body = "\n".join(lines)
        msg.set_content(body)

        return msg

    def _do_email(self, alert_list):
        msg = self._create_message(alert_list)
        smtp_obj = _get_smtp_object(self.email_settings)
        try:
            smtp_obj.send_message(msg)
        finally:
            smtp_obj.quit()

    def _email_loop(self):
        try:
            logger.debug("Email loop started")

            while True:
                if self.is_finished.is_set():
                    return

                # see if anything is ready for upload
                try:
                    alert_tuple, callback = self.alerts.popleft()
                except IndexError:
                    # short delay when empty; no need to max out CPU
                    time.sleep(0.1)
                    continue

                try:
                    self._do_email(alert_tuple)
                    callback(None)
                except Exception as e:
                    callback(e)
        except Exception:
            logger.exception("Uncaught exception in email_loop")
            self.stop()

    def send_alerts(self, serial_number, display_name, alert_list, callback):
        dt = datetime.datetime.utcnow()

        last = self.last_sent.get(serial_number)
        if last is None or (dt - last) >= datetime.timedelta(minutes=10):
            alert_tuple = (serial_number, display_name, alert_list, dt)
            self.alerts.append((alert_tuple, callback))
            self.last_sent[serial_number] = dt
        else:
            logger.debug("ignoring alert too soon after last sent email")

    def stop(self):
        self.is_finished.set()

    def join(self):
        self.email_thread.join()
