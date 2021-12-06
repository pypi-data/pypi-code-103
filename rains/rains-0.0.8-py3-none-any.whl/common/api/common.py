# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from flask import jsonify
from flask import request

from rains.common.db.sql_packaging import Sql
from rains.common.db.database import Database


# 数据库实例
db: Database = Database()


def get_request_parameters(*paras) -> dict:
    """
    获取请求参数

    * 解析请求接口时携带的参数。

    Args:
        paras (*): 需要解析的参数 Key, 允许传递多个值。

    Return:
        返回参数字典

    """
    try:
        request_handle = request.args
        if request.method == 'POST':
            request_handle = request.form

        return_para_dict = {}
        for para_key in paras:
            para_value = request_handle.get(para_key)
            return_para_dict.update({para_key: para_value})

        return return_para_dict

    except BaseException as e:
        raise Exception(f"接口解析参数时，发生异常:: { e }")


def successful(paras: dict or None) -> jsonify:
    """
    请求成功返回参数

    Args:
        paras (dict or None): 需要返回的数据字典

    Return:
        经过加工的数据结构

    """
    r_structure = {
        'code': 200,
        'message': '请求成功',
        'data': {}
    }

    if paras:
        r_structure.update({'data': paras})

    return jsonify(r_structure)


def unsuccessful(err_message: str) -> jsonify:
    """
    请求失败返回参数

    Args:
        err_message (str): 需要返回的错误信息

    Return:
        经过加工的数据结构

    """
    r_structure = {
        'code': 500,
        'message': '请求失败',
        'err': err_message
    }

    return jsonify(r_structure)
