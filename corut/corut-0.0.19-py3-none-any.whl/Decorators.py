#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Decorator functions have been developed to meet common needs.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

from datetime import timedelta
from time import time
from .Shell import print_error


def calculate_time_processing(function):
    """
    Calculates the completion time of the function sent to it and writes it as print.
    :param function:
    :return:
    """
    def caller_func(*args, **kwargs):
        start_time = time()
        data = function(*args, **kwargs)
        t = time() - start_time
        if t > 60:
            t = str(timedelta(seconds=int(t)))
        print(f'Function:{function.__name__} ---> Run Time Elapsed:{t}')
        return data
    return caller_func


def try_except(function):
    """
    It is used to produce practical solutions in functions that do not use try/except in the code.
    :param function:
    :return:
    """
    def caller_func(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except BaseException as error:
            print_error(error, locals())
            return None
    return caller_func
