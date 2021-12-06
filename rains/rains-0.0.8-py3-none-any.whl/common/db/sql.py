# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from rains.common.db.sql_packaging.sql_task import SqlTask
from rains.common.db.sql_packaging.sql_case import SqlCase


class Sql(object):
    """
    SQL语句

    * 动态拼接 SQLite 语句。

    """

    @property
    def task(self):
        """
        任务相关的 SQL 语句
        """
        return SqlTask

    @property
    def case(self):
        """
        用例相关的 SQL 语句
        """
        return SqlCase
