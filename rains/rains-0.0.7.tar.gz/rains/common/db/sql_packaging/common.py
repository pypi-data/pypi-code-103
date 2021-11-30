# !/usr/bin/env python
# coding:utf-8

# Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.

# Based on the Apache License 2.0 open source protocol.

__author__ = 'quinn.7@foxmail.com'


__all__ = [
    'ConstTaskAndCaseState',
    'ConstDatabaseTaskNaming',
    'ConstDatabaseCaseNaming',
    'ConstDatabaseTableNaming',
    '_get_desc_limit_section',
    '_machining_parameter',
]


from rains.common.const import ConstTaskAndCaseState
from rains.common.db.const import ConstDatabaseTaskNaming
from rains.common.db.const import ConstDatabaseCaseNaming
from rains.common.db.const import ConstDatabaseTableNaming


def _get_desc_limit_section(paras: dict):
    """
    获取数据返回量限制

    * 默认是获取 1 页， 10 条数据。

    """
    if 'page' not in paras.keys():
        paras['page'] = 1
    if 'number' not in paras.keys():
        paras['number'] = 10
    paras['page'] = int(paras['page'])
    paras['number'] = int(paras['number'])

    limit_begin = 0
    if paras['page'] > 1:
        limit_begin = (paras['page'] - 1) * paras['number']

    return f'LIMIT { limit_begin }, { paras["number"] }'


def _machining_parameter(paras: dict, essential_list: list):
    """
    检查参数是否缺失
    """
    if not paras:
        paras = {}

    for essential_para in essential_list:
        if paras[essential_para] is None:
            raise ParametersAreMissingException(essential_para)

    return paras


class ParametersAreMissingException(Exception):
    """
    参数缺失错误类
    """
    def __init__(self, missing_para_key):
        Exception.__init__(self, f'SQL必要参数 { missing_para_key } 缺失!')
