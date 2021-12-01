"""Datetime extensions.

Functions:
datetime_from_data
round_datetime
timedelta_split
"""

import datetime as dt

from dateutil import parser

from eagers.config.precision import \
    DATETIME_ROUNDING_PRECISION, DATETIME_ROUNDING_TIMEDELTA_FIELD as DRTF


def datetime_from_data(d):
    """Converts string values to datetime and rounds datetime values."""
    if isinstance(d, dt.datetime):
        return round_datetime(d)
    elif isinstance(d, str):
        return parser.parse(d)
    else:
        raise TypeError(
            f"Unrecognized type for datetime data: {type(d).__name__!r}")


def round_datetime(d, precision=DATETIME_ROUNDING_PRECISION):
    """Round a datetime to the named precision. If no precision is
    specified, the default datetime precision will be used.

    Cf. https://stackoverflow.com/a/3464000/7232335
    """
    # Add half the precision.
    d += dt.timedelta(**{f"{precision}s": 1}) / 2
    # "Floor" using next highest precision.
    d -= dt.timedelta(**{f"{DRTF}s": getattr(d, DRTF)})
    return d


def timedelta_split(tdelta):
    """Returns a list of length 4 with number of days, hours, minutes,
    and seconds in the given timedelta.
    """
    hours, seconds = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return [tdelta.days, hours, minutes, seconds + tdelta.microseconds / 1e6]
