import re

SENSITIVE_FIELDS = ["metastore_url", "username",
                    "password", "certificate", "apikey"]
MASK_STRING = "***"

class SensitiveDataFormatter(object):
    """
    Custom formatter for logging to mask sensitive fields
    """

    def __init__(self, orig_formatter, fields=None):
        self.orig_formatter = orig_formatter
        self.fields = fields

    def format(self, record):
        message = self.orig_formatter.format(record)
        # Mask sensitive fields in the message
        fields_to_mask = SENSITIVE_FIELDS
        if self.fields:
            fields_to_mask = SENSITIVE_FIELDS + self.fields
        message = self.mask_sensitive_fields(message, fields_to_mask)
        return message

    def mask_sensitive_fields(self, message: str, fields_to_mask: list):
        if message and fields_to_mask:
            for field in fields_to_mask:
                if field in message:
                    # Check if log message contains sensitive fields in the format 'field': 'sensitive_value'
                    # If found, replace the value with mask characters like 'field': '***'
                    pattern = "['\"]{}['\"]\s*:\s*['\"][^'\"]+['\"]".format(
                        field)
                    match = re.search(pattern, message)
                    if match:
                        match_str = match.group()
                        if match_str.startswith('"'):
                            replace_str = '"{}": "{}"'.format(
                                field, MASK_STRING)
                        else:
                            replace_str = "'{}': '{}'".format(
                                field, MASK_STRING)
                        message = message.replace(match_str, replace_str)
        return message

    def __getattr__(self, attr):
        return getattr(self.orig_formatter, attr)
