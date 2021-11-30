import smtplib
import email.message
from email import charset
import time


class Email:
    def __init__(self, host, logger):
        if not host and type(host) is not str:
            raise TypeError("Argument host must be string")
        self.smtp_server = smtplib.SMTP(host=host)
        self._logger = logger

    def send_email(self, from_addr, to_addr, subject, content):
        msg = email.message.Message()
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg.add_header("Content-Type", "text/html; charset=utf-8")
        msg.set_payload(
            content, charset=charset.Charset(input_charset="utf-8")
        )

        tries = 0
        while tries < 5:
            if tries > 0:
                time.sleep(3)  # 3 second wait between tries
            try:
                self.smtp_server.sendmail(
                    msg["From"], msg["To"], msg.as_string()
                )
                break
            except smtplib.SMTPServerDisconnected:
                tries += 1
                self._logger.log(
                    "ERROR",
                    f"Disconnected from smtp server. Attempt {tries} of 5",
                )
                self.smtp_server.connect(host=self.host)
                if tries == 5:
                    self._logger.log("ERROR", "Could not connect to host")
            except smtplib.SMTPSenderRefused:
                self._logger.log("ERROR", f"Could not send as {to_addr}")
                break
            except smtplib.SMTPRecipientsRefused as e:
                self._logger.log(
                    f"ERROR",
                    f"Could not send email to the following: {e.recipients}",
                )
                break
            except smtplib.SMTPDataError as e:
                self._logger.log(
                    f"ERROR",
                    f"Data refused in email. SMTP Error: {e.smtp_error}",
                )
