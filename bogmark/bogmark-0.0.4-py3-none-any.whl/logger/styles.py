import json
import logging

from .tools import get_extra_dict


class ExtraPercentStyle(logging.PercentStyle):
    def format(self, record):  # noqa
        record_data = record.__dict__
        formatted_string = self._fmt % record_data
        extra_dict = get_extra_dict(record)
        extra_string = " - ".join([f"{k}:{json.dumps(v, ensure_ascii=False)}" for k, v in extra_dict.items()])
        if extra_string:
            formatted_string += f" - EXTRA: {extra_string}"
        return formatted_string
