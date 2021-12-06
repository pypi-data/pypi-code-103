# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


__all__ = [
    'DB',
    'SQL',
    'Response',
    'Blueprint',
    'ServerParameter',
]


from flask import jsonify
from flask import request
from flask import Response
from flask import Blueprint

from rains.common.db.sql_lang import SqlLang
from rains.common.db.database import Database


# 通用实例
DB: Database = Database()
SQL: SqlLang = SqlLang()


class ServerParameter(object):
    """
    [ 服务端参数类 ]
    * 无

    """

    @staticmethod
    def analysis_request_paras(*paras) -> dict:
        """
        [ 解析请求参数 ]
        * 无

        [ 必要参数 ]
        * *paras (str) : 需要解析的参数 Key, 允许传递多个值

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (dict) : 返回解析成功的参数字典

        """

        try:
            # 解析请求模式
            request_handle = request.args
            if request.method == 'POST':
                request_handle = request.form

            # 获取参数并且返回
            decryption_paras = {}
            for key in paras:
                value = request_handle.get(key)
                if value is None:
                    pass
                else:
                    decryption_paras.update({key: value})
            return decryption_paras

        except BaseException as e:
            raise Exception(f"解析请求接口携带的参数异常:: { e }")

    @staticmethod
    def successful(paras: dict or None) -> jsonify:
        """
        [ 请求成功 ]
        * 无

        [ 必要参数 ]
        * paras （dict | none） : 需要返回的数据字典, 默认 None 则返回空字典

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (Json) : 经过加工的 Json 数据结构

        """

        r_structure = {
            'code': 200,
            'message': '成功',
            'data': {}
        }

        if paras:
            r_structure.update({'data': paras})

        return jsonify(r_structure)

    @staticmethod
    def unsuccessful(err: str) -> jsonify:
        """
        [ 请求失败 ]
        * 无

        [ 必要参数 ]
        * err (str) : 需要返回的错误信息

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (Json) : 经过加工的 Json 数据结构

        """

        r_structure = {
            'code': 500,
            'message': '失败',
            'err': err
        }

        return jsonify(r_structure)
