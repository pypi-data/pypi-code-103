# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


def singleton_pattern(cls, *args, **kwargs):
    """
    [ 单例模式装饰器 ]
    * 无

    """

    instances = {}

    def _singleton_pattern():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton_pattern
