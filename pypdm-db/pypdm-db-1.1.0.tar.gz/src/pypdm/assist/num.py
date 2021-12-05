#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : EXP
# -----------------------------------------------


def byte_to_str(value) :
    """
    byte 转 str。
    :param value: byte 值
    :return: str 字符串
    """
    if isinstance(value, bytes) :
        value = bytes.decode(value)
    return value
