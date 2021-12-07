# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Create: Mar 21, 2017
# Modified: Jan 22, 2021

import re


def check_email(email):
    """
    Check input email address is correct
    """
    pattern = r"^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$"
    return re.match(pattern, email) is not None


def check_phone(phone):
    """
    regular for phone number
    """
    pattern = r"^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$"
    return re.match(pattern, phone) is not None


def check_number(num):
    """
    regular for digital number
    """
    pattern = r"^[0-9]+$"
    return re.match(pattern, num) is not None


def check_float(num):
    """
    regular for float number
    """
    pattern = r"^[0-9]+\.*[0-9]*$"
    return re.match(pattern, num) is not None


def check_chn_characters(name):
    """
    regular for Chinese characters
    """
    pattern = u'^[\u4e00-\u9fa5]+$'
    return re.match(pattern, name) is not None


def check_en_word(name, is_first_capital=True):
    """
    regular for English words
    """
    pattern = ""
    if is_first_capital:
        pattern = r"^[A-Z][a-z]+$"
    else:
        pattern = r"^[a-z]+$"
    return re.match(pattern, name) is not None


def check_filepath(filepath):
    """
    regular for file path
    """
    pattern = r"^(\\|/|\.|\w).*"
    return re.match(pattern, filepath) is not None


def check_date(date):
    """
    matches a date in yyyy-mm-dd format from 1900-01-01 through 2099-12-31, with a choice of four separators.
    """
    pattern = r"^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$"
    return re.match(pattern, date) is not None


def check_time_24f(time):
    """
    matches a time in HH:mm:ss 24-hours clock
    """
    pattern = r"^(2[0-3]|[01]?[0-9]):([0-5]?[0-9]):([0-5]?[0-9])$"
    return re.match(pattern, time) is not None


def check_time_12f(time):
    pattern = r"^(1[0-2]|0?[1-9]):([0-5]?[0-9]):([0-5]?[0-9]) ([AP]M)?$"
    return re.match(pattern, time) is not None


def check_datetime(datetime):
    """
    combination of date and time, from 1900-01-01 00:00:00 to 2099-12-31 23:59:59
    """
    pattern = r"^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01]) " \
              r"(2[0-3]|[01]?[0-9]):([0-5]?[0-9]):([0-5]?[0-9])$"
    return re.match(pattern, datetime) is not None


def check_ipv4(ip):
    """
    check the format of IPv4
    """
    pattern = r"^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$"
    return re.match(pattern, ip) is not None
