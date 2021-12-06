# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


class ConstDatabaseTableNaming(object):
    """
    [ 数据库表命名 ]
    * 无

    """

    TASKS = 'tasks'
    """ 任务表命名 """

    CASES = 'cases'
    """ 用例表命名 """


class ConstDatabaseTaskNaming(object):
    """
    [ 数据库任务表字段命名 ]
    * 无

    """

    TID = 'tid'
    """ 任务记录编号 """

    NAME = 'name'
    """ 任务名称 """

    REMARK = 'remark'
    """ 任务备注信息 """

    EXECUTE_DATE = 'execute_date'
    """ 执行日期 """

    IS_COMPLETED = 'is_completed'
    """ 是否已完成 """

    START_TIME = 'start_time'
    """ 开始时间 """

    END_TIME = 'end_time'
    """ 结束时间 """

    SPEND_TIME_S = 'spend_time_s'
    """ 消耗时间(秒) """

    CASE_ALL = 'case_all'
    """ 所有用例计数 """

    CASE_PASS = 'case_pass'
    """ 成功的用例计数 """

    CASE_FAIL = 'case_fail'
    """ 失败的用例计数 """


class ConstDatabaseCaseNaming(object):
    """
    [ 数据库用例表字段命名 ]
    * 无

    """

    CID = 'cid'
    """ 用例记录编号 """

    TID = 'tid'
    """ 所属的任务记录编号 """

    NAME = 'name'
    """ 用例名称 """

    REMARK = 'remark'
    """ 用例备注信息 """

    STATE = 'state'
    """ 用例状态 """

    EXECUTE_DATE = 'execute_date'
    """ 执行日期 """

    START_TIME = 'start_time'
    """ 开始时间 """

    END_TIME = 'end_time'
    """ 结束时间 """

    SPEND_TIME_S = 'spend_time_s'
    """ 消耗时间(秒) """

    RUN_STEP = 'run_step'
    """ 运行步骤 """
