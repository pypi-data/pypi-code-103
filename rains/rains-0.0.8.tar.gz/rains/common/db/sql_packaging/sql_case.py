# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


__all__ = ['SqlCase']


from rains.common.db.sql_packaging.common import *


class SqlCase(object):
    """
    [ 用例相关的 SQL 语句 ]
    * 无
    
    """

    @staticmethod
    def get_count_all() -> str:
        """
        [ 查询所有用例数量 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句
        
        """
        
        return f""" 

        SELECT COUNT(id) FROM { ConstDatabaseTableNaming.CASES } 

        """

    @staticmethod
    def get_count_pass() -> str:
        """
        [ 查询所有通过的用例数量 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句
        
        """
        
        return f""" 

        SELECT COUNT(id) FROM { ConstDatabaseTableNaming.CASES }

        WHERE { ConstDatabaseCaseNaming.STATE } == '{ ConstTaskAndCaseState.SUCCESSFUL }'

        """

    @staticmethod
    def get_count_fail() -> str:
        """
        [ 查询所有状态为非'成功'用例数量 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句
        
        """
        
        return f""" 

        SELECT COUNT(id) FROM { ConstDatabaseTableNaming.CASES }

        WHERE { ConstDatabaseCaseNaming.STATE } != '{ ConstTaskAndCaseState.SUCCESSFUL }'

        """

    @staticmethod
    def get_count_from_data(paras: dict) -> str:
        """
        [ 查询指定日期里所有失败的用例数量 ]
        * 无

        [ 必要参数 ]
        * execute (str) : 执行日期

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句

        """

        DatabaseParameter.machining_parameter(
            paras,
            [
                ConstDatabaseCaseNaming.EXECUTE_DATE
            ]
        )

        return f""" 

        SELECT COUNT(id) FROM { ConstDatabaseTableNaming.CASES }

        WHERE { ConstDatabaseCaseNaming.EXECUTE_DATE } == '{ paras[ConstDatabaseCaseNaming.EXECUTE_DATE] }'

        """

    @staticmethod
    def get_count_fail_from_data(paras: dict) -> str:
        """
        [ 查询指定日期里所有失败的用例数量 ]
        * 无

        [ 必要参数 ]
        * execute (str) : 执行日期

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句
        
        """

        DatabaseParameter.machining_parameter(
            paras,
            [
                ConstDatabaseCaseNaming.EXECUTE_DATE
            ]
        )

        return f""" 

        SELECT COUNT(id) FROM { ConstDatabaseTableNaming.CASES }

        WHERE { ConstDatabaseCaseNaming.STATE } != '{ ConstTaskAndCaseState.SUCCESSFUL }'

        AND { ConstDatabaseCaseNaming.EXECUTE_DATE } == '{ paras[ConstDatabaseCaseNaming.EXECUTE_DATE] }'

        """

    @staticmethod
    def get_count_from_tid(paras: dict) -> str:
        """
        [ 查询指定任务下所有用例数量 ]
        * 无

        [ 必要参数 ]
        * tid (int) : 所属任务ID

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句

        """

        DatabaseParameter.machining_parameter(
            paras,
            [
                ConstDatabaseTaskNaming.TID
            ]
        )

        return f""" 

        SELECT COUNT(id) FROM { ConstDatabaseTableNaming.CASES } 

        WHERE { ConstDatabaseTaskNaming.TID } = { paras[ConstDatabaseTaskNaming.TID] }

        """

    @staticmethod
    def get_count_form_date(paras: dict) -> str:
        """
        [ 查询指定执行日期的用例数量 ]
        * 无

        [ 必要参数 ]
        * execute (str) : 执行日期

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句

        """

        DatabaseParameter.machining_parameter(
            paras,
            [
                ConstDatabaseTaskNaming.EXECUTE_DATE
            ]
        )

        return f""" 

        SELECT COUNT(id) FROM { ConstDatabaseTableNaming.CASES } 

        WHERE { ConstDatabaseTaskNaming.EXECUTE_DATE } = '{ paras[ConstDatabaseTaskNaming.EXECUTE_DATE] }'

        """

    @staticmethod
    def get_info_from_tid(paras: dict) -> str:
        """
        [ 查询所有用例详情信息列表 ]
        * 无

        [ 必要参数 ]
        * tid (int) : 所属任务ID

        [ 可选参数 ]
        * state (str) : 状态
        * page (int) : 页数
        * number (int) : 查询数量

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句

        """

        DatabaseParameter.machining_parameter(
            paras,
            [
                ConstDatabaseCaseNaming.TID
            ]
        )

        if ConstDatabaseCaseNaming.STATE in paras.keys():
            state = f'{ ConstDatabaseCaseNaming.STATE } = "{ paras[ConstDatabaseCaseNaming.STATE] }"'
        else:
            state = f'{ ConstDatabaseCaseNaming.STATE } in ("{ ConstTaskAndCaseState.BLOCK }", ' \
                    f'"{ ConstTaskAndCaseState.SUCCESSFUL }", "{ ConstTaskAndCaseState.UNSUCCESSFUL }")'

        return f"""

        SELECT * FROM { ConstDatabaseTableNaming.CASES }

        WHERE { state } AND { ConstDatabaseCaseNaming.TID } = { paras[ConstDatabaseCaseNaming.TID] }

        ORDER BY ID DESC

        { DatabaseParameter.get_desc_limit(paras) }

        """

    @staticmethod
    def get_info_from_cid(paras: dict) -> str:
        """
        [ 查询指定CID的用例详情信息 ]
        * 无

        [ 必要参数 ]
        * cid (int) : 用例ID

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句

        """

        DatabaseParameter.machining_parameter(
            paras,
            [
                ConstDatabaseCaseNaming.CID
            ]
        )

        return f"""

        SELECT * FROM { ConstDatabaseTableNaming.CASES }

        WHERE id = { paras[ConstDatabaseCaseNaming.CID] }

        """

    @staticmethod
    def add(paras: dict) -> str:
        """
        [ 创建用例 ]
        * 无

        [ 必要参数 ]
        * tid (int) : 所属任务记录ID
        * name (str) : 用例名称
        * remark (str) : 用例备注
        * execute_date (str) : 执行日期

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句

        """

        DatabaseParameter.machining_parameter(
            paras,
            [
                ConstDatabaseCaseNaming.TID,
                ConstDatabaseCaseNaming.NAME,
                ConstDatabaseCaseNaming.REMARK,
                ConstDatabaseCaseNaming.EXECUTE_DATE
            ]
        )

        return f""" 

        INSERT INTO { ConstDatabaseTableNaming.CASES } (

            id, 
            { ConstDatabaseCaseNaming.TID }, 
            { ConstDatabaseCaseNaming.NAME }, 
            { ConstDatabaseCaseNaming.REMARK }, 
            { ConstDatabaseCaseNaming.STATE }, 
            { ConstDatabaseCaseNaming.EXECUTE_DATE }, 
            { ConstDatabaseCaseNaming.START_TIME }, 
            { ConstDatabaseCaseNaming.END_TIME },
            { ConstDatabaseCaseNaming.SPEND_TIME_S },
            { ConstDatabaseCaseNaming.RUN_STEP }
        )

        VALUES (

            NULL,
            '{ paras[ConstDatabaseCaseNaming.TID] }',
            '{ paras[ConstDatabaseCaseNaming.NAME] }',
            '{ paras[ConstDatabaseCaseNaming.REMARK] }',
            '{ ConstTaskAndCaseState.BLOCK }', 
            '{ paras[ConstDatabaseCaseNaming.EXECUTE_DATE] }',
             NULL, 
             NULL,
             NULL,
             NULL
        )

        """

    @staticmethod
    def update(paras: dict) -> str:
        """
        [ 更新用例 ]
        * 无

        [ 必要参数 ]
        * cid (int) : 用例ID
        * state (str) : 用例状态
        * start_time (date) : 开始时间
        * end_time (date) : 结束时间
        * spend_time_s (int) : 消耗时间(秒)
        * run_step (str) : 运行步骤

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句

        """

        DatabaseParameter.machining_parameter(
            paras,
            [
                ConstDatabaseCaseNaming.CID,
                ConstDatabaseCaseNaming.STATE,
                ConstDatabaseCaseNaming.START_TIME,
                ConstDatabaseCaseNaming.END_TIME,
                ConstDatabaseCaseNaming.SPEND_TIME_S,
                ConstDatabaseCaseNaming.RUN_STEP
            ]
        )

        return f"""

        UPDATE { ConstDatabaseTableNaming.CASES }

        SET 
            { ConstDatabaseCaseNaming.STATE }         = '{ paras[ConstDatabaseCaseNaming.STATE] }',
            { ConstDatabaseCaseNaming.START_TIME }    = '{ paras[ConstDatabaseCaseNaming.START_TIME] }',
            { ConstDatabaseCaseNaming.END_TIME }      = '{ paras[ConstDatabaseCaseNaming.END_TIME] }',
            { ConstDatabaseCaseNaming.SPEND_TIME_S }  = '{ paras[ConstDatabaseCaseNaming.SPEND_TIME_S] }',
            { ConstDatabaseCaseNaming.RUN_STEP }      = '{ paras[ConstDatabaseCaseNaming.RUN_STEP] }'

        WHERE
            ID = { paras[ConstDatabaseCaseNaming.CID] }

        """

    @staticmethod
    def delete_from_cid(paras: dict) -> str:
        """
        [ 删除指定CID用例 ]
        * 无

        [ 必要参数 ]
        * cid (int) : 用例ID

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句

        """

        DatabaseParameter.machining_parameter(
            paras, 
            [
                ConstDatabaseCaseNaming.CID
            ]
        )

        return f"""

        DELETE FROM { ConstDatabaseTableNaming.CASES }

        WHERE ID = { paras[ConstDatabaseCaseNaming.CID] }

        """

    @staticmethod
    def delete_from_tid(paras: dict = None) -> str:
        """
        [ 删除指定TID所有用例 ]
        * 无

        [ 必要参数 ]
        * tid (int) : 所属任务ID

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句

        """

        DatabaseParameter.machining_parameter(
            paras,
            [
                ConstDatabaseTaskNaming.TID
            ]
        )

        return f"""

        DELETE FROM { ConstDatabaseTableNaming.CASES }

        WHERE TID = { paras[ConstDatabaseTaskNaming.TID] }

        """

    @staticmethod
    def delete_all() -> str:
        """
        [ 删除所有用例 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (str) : 拼接完的 SQL 语句

        """

        return f"""

        DELETE FROM { ConstDatabaseTableNaming.CASES }

        """
