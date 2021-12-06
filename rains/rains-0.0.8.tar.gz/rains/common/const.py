# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


import pathlib


class ConstFileNaming(object):
    """
    [ 文件命名 ]
    * 无

    """

    LOGS = 'logs'
    """ 项目日志目录 """

    DATA = 'data'
    """ 项目数据目录 """

    DB = 'database.db'
    """ 数据库文件 """


class ConstPath(object):
    """
    [ 路径 ]
    * 无

    """

    ROOT = pathlib.Path().cwd()
    """ 项目根 """

    LOGS = ROOT.joinpath(ConstFileNaming.LOGS)
    """ 日志目录 """

    DATA = ROOT.joinpath(ConstFileNaming.DATA)
    """ 数据目录 """

    DB = DATA.joinpath(ConstFileNaming.DB)
    """ 数据库文件 """


class ConstProjectType(object):
    """
    [ 项目类型 ]
    * 无

    """

    WEB = 'PROJECT_TYPE_FROM_WEB'
    """ WEB """

    MINI = 'PROJECT_TYPE_FROM_MINI'
    """ 微信小程序 """


class ConstTaskType(object):
    """
    [ 任务类型 ]
    * 无

    """

    CODE = 'TASK_TYPE_FROM_CODE'
    """ 代码译文 """

    JSON = 'TASK_TYPE_FROM_JSON'
    """ JSON译文 """


class ConstTaskAndCaseState(object):
    """
    [ 任务与用例的状态 ]
    * 无

    """
    BLOCK = '堵塞'
    """ 堵塞 """

    ANOMALY = '异常'
    """ 异常 """

    SUCCESSFUL = '成功'
    """ 成功 """

    UNSUCCESSFUL = '失败'
    """ 失败 """


class ConstTaskOrderSignNaming(object):
    """
    [ 任务流程指令命名 ]
    * 无

    """

    CLASS_STARTING = 'set_class_starting'
    """ 类级起点 """

    CLASS_ENDING = 'set_class_ending'
    """ 类级终点 """

    FUNCTION_STARTING = 'set_function_starting'
    """ 函数级起点 """

    FUNCTION_ENDING = 'set_function_ending'
    """ 函数级终点 """
