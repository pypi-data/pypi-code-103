# -*- coding: utf-8 -*-

import os
import arrow
from hurry.filesize import size


def datetimeformat(date_str):
    dt = arrow.get(date_str)
    return dt.humanize()


def file_name(key):
    return os.path.basename(key)


def folder_name(key):
    return os.path.basename(os.path.normpath(key)) + "/"


def file_size(key):
    return size(key)
