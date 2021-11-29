#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It has been developed to simplify all Date & Time operations.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

from datetime import datetime, timedelta
from .Shell import print_error


def check_date_format_from_string(data):
    if str(data).replace(':', '').replace('.', '').isdigit() and len(str(data).split(':')) == 3:
        return True
    else:
        return False


def get_date_time(
        data=None, date_format='%Y/%m/%d %H:%M:%S.%f', convert_to_str=True,
        weeks=0, days=0, hours=0, minutes=0, seconds=0, microseconds=0, milliseconds=0
):
    """
    It converts the data entered in the formats frame into datetime format.
    :param data: Datetime data in formatted string type
    :param date_format: The format of the data
    :param convert_to_str: Used to return as string in the same format
    :param weeks: If you want to add additional week information
    :param days: If you want to add additional days information
    :param hours: If you want to add additional hours information
    :param minutes: If you want to add additional minutes information
    :param seconds: If you want to add additional seconds information
    :param microseconds: If you want to add additional microseconds information
    :param milliseconds: If you want to add additional milliseconds information
    :return: returns date/time information
    """
    try:
        if data is None:
            data = datetime.now()
        if isinstance(data, str):
            data = datetime.strptime(data, date_format)
        data = data + timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)
        if convert_to_str:
            data = datetime.strftime(data, date_format)
    except Exception as error:
        print_error(error, locals())
    return data


def seconds_to_string(data):
    """
    translates second data in day, seconds, hours, minutes, seconds
    :rtype: object
    """
    try:
        if isinstance(data, int) or isinstance(data, float):
            return str(timedelta(seconds=int(data)))
        else:
            return str(data)
    except Exception as error:
        print_error(error, locals())
        return None


def string_to_hours(duration):
    try:
        if not isinstance(duration, int) and check_date_format_from_string(duration):
            duration = int(float(time_to_seconds(duration, date_format='%H:%M:%S')))
        duration = divmod(duration, 3600)
        if duration[0] > 0:
            duration = f'{duration[0]} hours'
        else:
            duration = f'{int(float(divmod(int(float(duration[1])), 60)[0]))} minutes'
    except Exception as error:
        print_error(error, locals())
    return duration


def time_to_seconds(data, date_format=None):
    try:
        if date_format:
            data = string_to_date_time(data, date_format=date_format)
        hour = data.hour * 60 * 60
        minute = data.minute * 60
        second = data.second
        microsecond = str(data.microsecond)[:2]
        total_second = f'{hour + minute + second }.{microsecond}'
        return float(total_second)
    except Exception as error:
        print_error(error, locals())
        return 0.0


class DateTime:
    check_date_format_from_string = staticmethod(check_date_format_from_string)
    get_date_time = staticmethod(get_date_time)
    seconds_to_string = staticmethod(seconds_to_string)
    string_to_hours = staticmethod(string_to_hours)
    time_to_seconds = staticmethod(time_to_seconds)
