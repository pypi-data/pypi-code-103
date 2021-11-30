import logging
import warnings
from collections.abc import MutableMapping

from .configs import rec_default_variables


def get_extra_dict(rec):
    extra_dict = {}
    extra_data_keys = set(rec.__dict__) - rec_default_variables
    if extra_data_keys:
        for extra_key in extra_data_keys:
            extra_record = rec.__dict__[extra_key]
            if not isinstance(extra_record, (str, float, int)):
                raise TypeError("extra values should be one of: str, float, int")
            extra_dict[extra_key] = extra_record
    return extra_dict


def disable_noise(custom_noisy_loggers=()):
    warnings.simplefilter("ignore")
    for logger_name in list(custom_noisy_loggers):
        logging.getLogger(logger_name).setLevel("CRITICAL")


def flatten(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
