# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from rains.common.decorator import singleton_pattern


@singleton_pattern
class CaseRecorder(object):
    """
    [ 用例记录器 ]
    * 该模块负责记录用例执行时产生的日志，并且暂存至下一次读取。

    """

    _record_dict: dict
    """ 记录列表字典 """

    def __init__(self):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._record_dict = {}

    @property
    def record_dict(self):

        return self._record_dict

    def write(self, core_id: int, record: str):
        """
        [ 录入 ]
        * 无

        [ 必要参数 ]
        * core_id (int) : 核心ID
        * record (str) : 录入的信息

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        if core_id in self.record_dict:
            self.record_dict.update({core_id: ''.join([self.record_dict[core_id], '\n', record])})

        else:
            self.record_dict[core_id] = record

    def read(self, core_id) -> str:
        """
        [ 读取 ]
        * 读取后，缓冲器会清空所有暂存数据。

        [ 必要参数 ]
        * core_id (int) : 核心ID
        * record (str) : 录入的信息

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 所有记录拼接成的字符串

        """

        return_record_str = self._record_dict[core_id]

        del self._record_dict[core_id]

        return return_record_str
