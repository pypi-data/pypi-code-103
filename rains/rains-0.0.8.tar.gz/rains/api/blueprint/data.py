# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from rains.api.common import *
from rains.common.db.const import ConstDatabaseTaskNaming
from rains.common.db.const import ConstDatabaseCaseNaming


# 数据接口蓝图
data_blueprint = Blueprint('data', __name__)


@data_blueprint.route('/data/summarize', methods=['GET'])
def summarize() -> Response:
    """
    [ 获取执行信息概述 ]
    * 无

    [ 必要参数 ]
    * 无

    [ 可选参数 ]
    * 无

    [ 返回内容 ]
    * (Response) : 执行信息概述

    """

    try:
        # 获取最新执行数据
        new_exec_data = {}
        # 获取日期
        date = DB.read(SQL.task.get_date_list())[0][0]
        new_exec_data.update({'date': date})
        # 获取任务数量
        new_exec_data.update({'task_count': DB.read(SQL.task.get_count_from_data({
            ConstDatabaseTaskNaming.EXECUTE_DATE: date}))[0][0]})
        # 获取用例数量
        new_exec_data.update({'case_count': DB.read(SQL.case.get_count_from_data({
            ConstDatabaseCaseNaming.EXECUTE_DATE: date}))[0][0]})
        # 获取异常用例数量
        new_exec_data.update({'fail_case_count': DB.read(SQL.case.get_count_fail_from_data({
            ConstDatabaseTaskNaming.EXECUTE_DATE: date}))[0][0]})
        # 获取消耗时间
        new_exec_data.update({'spend_time': round((DB.read(SQL.task.get_spend_time_from_data({
            ConstDatabaseTaskNaming.EXECUTE_DATE: date}))[0][0] / 60), 2)})

        # 获取历史执行数据
        history_exec_data = {}
        # 获取任务数量
        history_exec_data.update({'task_count': DB.read(SQL.task.get_count_all())[0][0]})
        # 获取用例数量
        history_exec_data.update({'case_count': DB.read(SQL.case.get_count_all())[0][0]})
        # 获取异常用例数量
        history_exec_data.update({'fail_case_count': DB.read(SQL.case.get_count_fail())[0][0]})
        # 获取消耗时间
        history_exec_data.update({'spend_time': round((DB.read(SQL.task.get_spend_time_all())[0][0] / 60), 2)})
        # 获取异常任务数量
        history_exec_data.update({'fail_task_count': DB.read(SQL.task.get_count_fail())[0][0]})

        return ServerParameter.successful({
            'new_exec': new_exec_data,
            'history_exec': history_exec_data
        })

    except BaseException as e:
        return ServerParameter.unsuccessful(f'{ e }')
