# coding=utf-8
from __future__ import absolute_import, print_function


class Context(dict):

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
