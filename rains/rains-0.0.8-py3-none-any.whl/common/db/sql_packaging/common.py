# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


__all__ = [
    'DatabaseParameter',
    'ConstTaskAndCaseState',
    'ConstDatabaseTaskNaming',
    'ConstDatabaseCaseNaming',
    'ConstDatabaseTableNaming',
]


from rains.common.const import ConstTaskAndCaseState
from rains.common.db.const import ConstDatabaseTaskNaming
from rains.common.db.const import ConstDatabaseCaseNaming
from rains.common.db.const import ConstDatabaseTableNaming


class DatabaseParameter(object):
    """
    [ 数据库参数类 ]
    * 无

    """

    @staticmethod
    def get_desc_limit(paras: dict or None) -> str:
        """
        [ 获取数据返回量区间限制 ]
        * 默认是获取 1 页， 10 条数据。

        [ 必要参数 ]
        * paras (dict | none) : 参数字典

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接好的 SQL LIMIT 语句

        """

        # 获取参数
        paras = {} if not paras else paras
        page = 1 if 'page' not in paras.keys() else int(paras['page'])
        number = 10 if 'number' not in paras.keys() else int(paras['number'])

        # 计算偏移量
        limit_begin = 0
        if page > 1:
            limit_begin = (page - 1) * number

        return f'LIMIT { limit_begin }, { number }'

    @staticmethod
    def machining_parameter(base_paras: dict, must_keys: list):
        """
        [ 检查参数是否包含必要 key ]
        * 如果 must_keys 的所有元素都存在于 base_paras 中，则通过，否则抛出 ParametersAreMissingException 异常。

        [ 必要参数 ]
        * base_paras (dict) : 参数字典
        * must_keys (list) : 必要 key 列表

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        base_paras = {} if not base_paras else base_paras

        for key in must_keys:
            try:
                if base_paras[key] is None:
                    pass
            except KeyError:
                raise ParametersAreMissingException(key)


class ParametersAreMissingException(Exception):
    """
    [ 参数缺失错误 ]
    * 无

    """

    def __init__(self, missing_para_key):
        Exception.__init__(self, f'数据库必要参数 { missing_para_key } 缺失!')
