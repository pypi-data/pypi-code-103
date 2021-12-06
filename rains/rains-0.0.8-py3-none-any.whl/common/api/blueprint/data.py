# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from flask import Blueprint

from rains.common.db.const import ConstDatabaseTaskNaming
from rains.common.db.const import ConstDatabaseCaseNaming


data = Blueprint('data', __name__)


@data.route('/data/summarize', methods=['GET'])
def summarize():
    """
    返回执行信息概览
    """
    try:
        # 获取最新执行数据
        new_exec_data = {}
        # 获取日期
        date = db.read(Sql.tasks_get_date_list())[0][0]
        new_exec_data.update({'date': date})
        # 获取任务数量
        new_exec_data.update({'task_count': db.read(Sql.tasks_get_count_from_data({
            ConstDatabaseTaskNaming.EXECUTE_DATE: date}))[0][0]})
        # 获取用例数量
        new_exec_data.update({'case_count': db.read(Sql.cases_get_count_form_data({
            ConstDatabaseCaseNaming.EXECUTE_DATE: date}))[0][0]})
        # 获取异常用例数量
        new_exec_data.update({'fail_case_count': db.read(Sql.cases_get_all_count_in_fail_from_data({
            ConstDatabaseTaskNaming.EXECUTE_DATE: date}))[0][0]})
        # 获取消耗时间
        new_exec_data.update({'spend_time': round((db.read(Sql.tasks_get_spend_time_from_data({
            ConstDatabaseTaskNaming.EXECUTE_DATE: date}))[0][0] / 60), 2)})

        # 获取历史执行数据
        history_exec_data = {}
        # 获取任务数量
        history_exec_data.update({'task_count': db.read(Sql.tasks_get_count())[0][0]})
        # 获取用例数量
        history_exec_data.update({'case_count': db.read(Sql.cases_get_all_count())[0][0]})
        # 获取异常用例数量
        history_exec_data.update({'fail_case_count': db.read(Sql.cases_get_all_count_in_fail())[0][0]})
        # 获取消耗时间
        history_exec_data.update({'spend_time': round((db.read(Sql.tasks_get_spend_time())[0][0] / 60), 2)})
        # 获取异常任务数量
        history_exec_data.update({'fail_task_count': db.read(Sql.tasks_get_count_in_fail())[0][0]})

        return successful(paras={
            'new_exec': new_exec_data,
            'history_exec': history_exec_data
        })

    except BaseException as e:
        return unsuccessful(f'{ e }')
