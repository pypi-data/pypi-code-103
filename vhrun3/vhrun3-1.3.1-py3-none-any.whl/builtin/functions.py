"""
Built-in functions used in YAML/JSON testcases.
"""

import datetime
import random
import re
import string
import time
import os, threading

import jmespath

from vhrun3.exceptions import ParamsError


def gen_random_string(str_len):
    """ generate random string with specified length
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len)
    )


def get_timestamp(str_len=13):
    """ get timestamp string, length can only between 0 and 16
    """
    if isinstance(str_len, int) and 0 < str_len < 17:
        return str(time.time()).replace(".", "")[:str_len]

    raise ParamsError("timestamp length can only between 0 and 16.")


def get_current_date(fmt="%Y-%m-%d"):
    """ get current date, default format is %Y-%m-%d
    """
    return datetime.datetime.now().strftime(fmt)


def sleep(n_secs):
    """ sleep n seconds
    """
    time.sleep(n_secs)


def get_process_thread_id():
    return "-{}-{}".format(os.getpid(), threading.currentThread().ident)


def set_os_environ(var_name, var_value):
    env_name = var_name + get_process_thread_id()
    os.environ[env_name] = var_value
    return var_name


def unset_os_environ(var_name):
    env_name = var_name + get_process_thread_id()
    os.environ.pop(env_name)


def get_os_environ(var_name):
    env_name = var_name + get_process_thread_id()
    return os.environ.get(env_name)


def check_status(environ_name, expr, response: dict, expect):
    ret = re.findall(r'.index\d+', expr)
    for item in ret:
        index = item.split(".index")[-1]
        expr = expr.replace(item, '[{}]'.format(index))
    status = jmespath.search(expr, response)
    if status == expect:
       unset_os_environ(environ_name)
    return status
