import logging
import re


class SecureLogFormatter(logging.Formatter):
    def format(self, record):
        self._patterns = []
        msg = super(SecureLogFormatter, self).format(record)
        msg = re.sub(
            r"[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]", "***REMOVED***", msg
        )
        return msg

    def __getattr__(self, attr):
        return getattr(self.orig_formatter, attr)
