# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Create: May 31, 2018
# Modified: Jan 22, 2021

import platform

from enum import Enum

from siki.basics import FileUtils
from siki.basics import Convert
from siki.basics import TimeTicker
from siki.basics import Hashcode
from siki.basics.Exceptions import NullPointerException, InvalidParamException


class Priority(Enum):
    INFO = 0
    DEBUG = 1
    WARNING = 2
    ERROR = 3


def _compute_base64(data: bytes):
    import base64

    # To be extra safe in python 3, encode text conditionally before concatenating with pad.
    if isinstance(data, str):
        data = data.encode('utf-8')

    if not isinstance(data, bytes):
        raise InvalidParamException("The parameter is neither a string nor byte array type")

    r = base64.b64encode(data)
    return Convert.binary_to_string(r)


def _priority_name(priority):
    if type(priority) is not Priority:
        raise InvalidParamException("'priority' must be an instance of Priority")
    if priority == Priority.INFO:
        return "INFO"
    elif priority == Priority.DEBUG:
        return "DEBUG"
    elif priority == Priority.WARNING:
        return "WARNING"
    elif priority == Priority.ERROR:
        return "ERROR"
    else:
        return "UNKNOWN"


def _gen_logfile(directory, file):
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d")

    return FileUtils.gen_file_path(directory, file, "log", timestamp)


def _check_valid_file(directory, file):
    if directory is None or file is None:
        raise NullPointerException("Invalid operation, call init first")

    return _gen_logfile(directory, file)


class Logger(object):

    def __init__(self, b_stdout=True, b_log=False, directory=None, file=None):
        self.m_bStdOut = b_stdout
        self.m_bUseLog = b_log
        if self.m_bUseLog:
            FileUtils.mkdir(directory)
            self.m_file = file
            self.m_dir = directory

    def file_path(self):
        return _check_valid_file(self.m_dir, self.m_file)

    def message(self, priority, title=None, msg=None, exception=None):
        import traceback

        # check log is validate
        if self.m_bUseLog:
            self.m_file = _check_valid_file(self.m_dir, self.m_file)

        error_line = "{0} <{1}>".format(TimeTicker.time_with_msg(), _priority_name(priority))

        if title is not None:
            error_line += "\t[{0}]".format(title)

        if msg is not None:
            error_line += "\t{0}".format(msg)

        # if SystemUtils.is_windows():
        if "Windows" in platform.system():
            error_line += "\r\n"
        else:
            error_line += "\n"

        if exception is not None:
            error = ''.join(
                traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
            error_line += "{0}".format(error)

        if self.m_bUseLog:
            FileUtils.write_file(self.m_file, Convert.string_to_binary(error_line), True)

        if self.m_bStdOut:
            print(error_line)

    def data_in_base64(self, priority, title: str, data: bytes):
        # check log is validate
        f = _check_valid_file(self.m_dir, self.m_file)
        line = "{0} <{1}> [{2}]".format(TimeTicker.time_with_msg(), _priority_name(priority), title)

        # if SystemUtils.is_windows():
        if "Windows" in platform.system():
            line += "\r\n    Data: {0}\r\n".format(_compute_base64(data))
        else:
            line += "\n    Data: {0}\n".format(_compute_base64(data))

        if self.m_bUseLog:
            FileUtils.write_file(f, Convert.string_to_binary(line), True)

        if self.m_bStdOut:
            print(line)

    def data_in_hashcode(self, priority, title: str, data: bytes):
        # check log is validate
        f = _check_valid_file(self.m_dir, self.m_file)
        line = "{0} <{1}> [{2}]".format(TimeTicker.time_with_msg(), _priority_name(priority), title)

        # if SystemUtils.is_windows():
        if "Windows" in platform.system():
            line += "\r\n    Data: {0}\r\n".format(Hashcode.md5(data))
        else:
            line += "\n    Data: {0}\n".format(Hashcode.md5(data))

        if self.m_bUseLog:
            FileUtils.write_file(f, Convert.string_to_binary(line), True)

        if self.m_bStdOut:
            print(line)


if __name__ == "__main__":
    log = Logger(False, True, "logs", "test")

    try:
        raise NullPointerException("invalid ptr")
    except Exception as e:
        log.message(Priority.INFO, "title", "check message", e)

    print(log.file_path())

    raw = FileUtils.read_file("callback.py")
    log.data_in_base64(Priority.INFO, "data", raw)

    log.data_in_hashcode(Priority.ERROR, "hashcode", raw)
