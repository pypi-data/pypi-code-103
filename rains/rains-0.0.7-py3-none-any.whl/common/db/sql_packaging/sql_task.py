# !/usr/bin/env python
# coding:utf-8

# Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.

# Based on the Apache License 2.0 open source protocol.

__author__ = 'quinn.7@foxmail.com'


from rains.common.db.sql_packaging.common import *


class SqlTask(object):
    """
    任务相关的 SQL 语句
    """

    @staticmethod
    def get_count_all() -> str:
        """
        查询所有任务数量
        """
        return f""" 

        SELECT COUNT(id)

        FROM { ConstDatabaseTableNaming.TASKS }

        """

    @staticmethod
    def get_count_pass() -> str:
        """
        查询全部通过的任务数量
        """
        return f""" 

        SELECT COUNT(id)

        FROM { ConstDatabaseTableNaming.TASKS }

        WHERE { ConstDatabaseTaskNaming.CASE_FAIL } == 0

        """

    @staticmethod
    def get_count_fail() -> str:
        """
        查询存在异常的任务数量
        """
        return f""" 

        SELECT COUNT(id)

        FROM { ConstDatabaseTableNaming.TASKS }

        WHERE { ConstDatabaseTaskNaming.CASE_FAIL } != 0

        """

    @staticmethod
    def get_count_from_data(paras: dict = None) -> str:
        """
        查询指定日期中的任务数量

        参数:
            * execute (str): 执行日期，不可为空

        """
        # 处理参数
        paras = _machining_parameter(paras, [ConstDatabaseTaskNaming.EXECUTE_DATE])

        return f""" 

        SELECT COUNT(id)

        FROM { ConstDatabaseTableNaming.TASKS }

        WHERE { ConstDatabaseTaskNaming.EXECUTE_DATE } = '{ paras[ConstDatabaseTaskNaming.EXECUTE_DATE] }'

        """

    @staticmethod
    def get_date_list(paras: dict = None) -> str:
        """
        查询去重后的所有存在任务的日期列表

        参数:
            * page (int): 页数
            * number (int): 查询个数

        """
        # 处理参数
        paras = _machining_parameter(paras, [])
        # 获取数据返回量限制
        limit = _get_desc_limit_section(paras)

        return f"""

        SELECT DISTINCT { ConstDatabaseTaskNaming.EXECUTE_DATE } 

        FROM { ConstDatabaseTableNaming.TASKS }

        ORDER BY ID DESC

        { limit }

        """

    @staticmethod
    def get_spend_time_all() -> str:
        """
        查询所有任务的消耗时间
        """
        return f""" 

        SELECT SUM({ ConstDatabaseTaskNaming.SPEND_TIME_S })

        FROM { ConstDatabaseTableNaming.TASKS }

        """

    @staticmethod
    def get_spend_time_from_data(paras: dict = None) -> str:
        """
        查询指定日期中所有任务的消耗时间

        参数:
            * execute (str): 执行日期，不可为空

        """
        # 处理参数
        paras = _machining_parameter(paras, [ConstDatabaseTaskNaming.EXECUTE_DATE])

        return f""" 

        SELECT SUM({ ConstDatabaseTaskNaming.SPEND_TIME_S })

        FROM { ConstDatabaseTableNaming.TASKS }

        WHERE { ConstDatabaseTaskNaming.EXECUTE_DATE } = '{ paras[ConstDatabaseTaskNaming.EXECUTE_DATE] }'

        """

    @staticmethod
    def get_info_all(paras: dict = None) -> str:
        """
        查询所有任务详情信息

        参数:
            * page (int): 页数
            * number (int): 查询个数

        """
        # 处理参数
        paras = _machining_parameter(paras, [])
        # 获取数据返回量限制
        limit = _get_desc_limit_section(paras)

        return f"""

        SELECT * 

        FROM { ConstDatabaseTableNaming.TASKS }

        ORDER BY ID DESC 

        { limit }

        """

    @staticmethod
    def get_info_from_tid(paras: dict = None) -> str:
        """
        查询指定TID的任务详情信息

        参数:
            * tid (int): 任务ID，不可为空

        """
        # 处理参数
        paras = _machining_parameter(paras, [ConstDatabaseCaseNaming.TID])

        return f"""

        SELECT *

        FROM { ConstDatabaseTableNaming.TASKS }

        WHERE ID = { paras[ConstDatabaseCaseNaming.TID] }

        """

    @staticmethod
    def add(paras: dict = None) -> str:
        """
        创建任务

        参数:
            * name (str): 任务名称，不可为空
            * remark (str): 任务备注，不可为空
            * execute_date (date): 执行日期，不可为空

        """
        # 处理参数
        paras = _machining_parameter(paras,
                                     [
                                         ConstDatabaseTaskNaming.NAME,
                                         ConstDatabaseTaskNaming.REMARK,
                                         ConstDatabaseTaskNaming.EXECUTE_DATE
                                     ])

        return f""" 

        INSERT INTO { ConstDatabaseTableNaming.TASKS } (

             id, 
             { ConstDatabaseTaskNaming.NAME },
             { ConstDatabaseTaskNaming.REMARK },
             { ConstDatabaseTaskNaming.EXECUTE_DATE },
             { ConstDatabaseTaskNaming.IS_COMPLETED },
             { ConstDatabaseTaskNaming.START_TIME },
             { ConstDatabaseTaskNaming.END_TIME },
             { ConstDatabaseTaskNaming.SPEND_TIME_S },
             { ConstDatabaseTaskNaming.CASE_ALL },
             { ConstDatabaseTaskNaming.CASE_PASS },
             { ConstDatabaseTaskNaming.CASE_FAIL }
        )

        VALUES (

            NULL,
            '{ paras[ConstDatabaseTaskNaming.NAME] }',
            '{ paras[ConstDatabaseTaskNaming.REMARK] }',
            '{ paras[ConstDatabaseTaskNaming.EXECUTE_DATE] }',
             0, NULL, NULL, NULL, NULL, NULL, NULL
        )

        """

    @staticmethod
    def update(paras: dict = None) -> str:
        """
        更新任务

        参数:
            * tid (int): 所属任务ID，不可为空
            * is_completed (bool): 是否已完成，不可为空
            * start_time (date): 开始时间，不可为空
            * end_time (date): 结束时间，不可为空
            * spend_time_s (int): 花费时间(秒)，不可为空
            * case_all (int): 所有用例数，不可为空
            * case_pass (int): 成功的用例数，不可为空
            * case_fail (int): 失败用例数量，不可为空

        """
        # 处理参数
        paras = _machining_parameter(paras,
                                     [
                                         ConstDatabaseTaskNaming.TID,
                                         ConstDatabaseTaskNaming.IS_COMPLETED,
                                         ConstDatabaseTaskNaming.START_TIME,
                                         ConstDatabaseTaskNaming.END_TIME,
                                         ConstDatabaseTaskNaming.SPEND_TIME_S,
                                         ConstDatabaseTaskNaming.CASE_ALL,
                                         ConstDatabaseTaskNaming.CASE_PASS,
                                         ConstDatabaseTaskNaming.CASE_FAIL
                                     ])

        return f"""

        UPDATE { ConstDatabaseTableNaming.TASKS }

        SET
            { ConstDatabaseTaskNaming.IS_COMPLETED }  = { paras[ConstDatabaseTaskNaming.IS_COMPLETED] },
            { ConstDatabaseTaskNaming.START_TIME }    = '{ paras[ConstDatabaseTaskNaming.START_TIME] }',
            { ConstDatabaseTaskNaming.END_TIME }      = '{ paras[ConstDatabaseTaskNaming.END_TIME] }',
            { ConstDatabaseTaskNaming.SPEND_TIME_S }  = '{ paras[ConstDatabaseTaskNaming.SPEND_TIME_S] }',
            { ConstDatabaseTaskNaming.CASE_ALL }      =  { paras[ConstDatabaseTaskNaming.CASE_ALL] },
            { ConstDatabaseTaskNaming.CASE_PASS }     =  { paras[ConstDatabaseTaskNaming.CASE_PASS] },
            { ConstDatabaseTaskNaming.CASE_FAIL }     =  { paras[ConstDatabaseTaskNaming.CASE_FAIL] }

        WHERE ID = { paras[ConstDatabaseTaskNaming.TID] }

        """

    @staticmethod
    def delete(paras: dict = None) -> str:
        """
        删除任务

        参数:
            * tid (int): 所属任务ID，不可为空

        """
        # 处理参数
        paras = _machining_parameter(paras, [ConstDatabaseTaskNaming.TID])

        return f"""

        DELETE FROM { ConstDatabaseTableNaming.TASKS }

        WHERE ID = { paras[ConstDatabaseTaskNaming.TID] }

        """

    @staticmethod
    def delete_all() -> str:
        """
        删除所有的任务

        """
        # 处理参数
        return f"""

        DELETE FROM { ConstDatabaseTableNaming.TASKS }

        """
