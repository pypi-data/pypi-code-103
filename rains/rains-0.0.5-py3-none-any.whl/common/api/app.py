# !/usr/bin/env python
# coding:utf-8

# Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.

# Based on the Apache License 2.0 open source protocol.

__author__ = 'quinn.7@foxmail.com'


import math

from flask import Flask
from flask import render_template

from rains.common.api.common import *

from rains.common.api.blueprint.data import data
from rains.common.api.blueprint.task import task
from rains.common.api.blueprint.case import case

from rains.common.db.const import ConstDatabaseTaskNaming
from rains.common.db.const import ConstDatabaseCaseNaming


app = Flask(__name__)
app.register_blueprint(data)
app.register_blueprint(task)
app.register_blueprint(case)
app.config['JSON_AS_ASCII'] = False
app._static_folder = './static'


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    """
    首页
    """
    page_data = {}

    new_exec_data = db.read(Sql.tasks_get_date_list())[0][0]
    page_data.update({'PageName': 'Index'})
    page_data.update({'NewExecData': new_exec_data})

    page_data.update({'NewTaskCount': db.read(Sql.tasks_get_count_from_data({
        ConstDatabaseTaskNaming.EXECUTE_DATE: new_exec_data
    }))[0][0]})
    page_data.update({'NewCaseCount': db.read(Sql.cases_get_count_form_data({
        ConstDatabaseCaseNaming.EXECUTE_DATE: new_exec_data
    }))[0][0]})
    page_data.update({'NewCaseFailCount': db.read(Sql.cases_get_all_count_in_fail_from_data({
        ConstDatabaseTaskNaming.EXECUTE_DATE: new_exec_data
    }))[0][0]})
    page_data.update({'NewSpendTime': round((db.read(Sql.tasks_get_spend_time_from_data({
        ConstDatabaseTaskNaming.EXECUTE_DATE: new_exec_data
    }))[0][0] / 60), 2)})

    page_data.update({'HistoryTaskCount': db.read(Sql.tasks_get_count())[0][0]})
    page_data.update({'HistoryCaseCount': db.read(Sql.cases_get_all_count())[0][0]})
    page_data.update({'HistoryCaseFailCount': db.read(Sql.cases_get_all_count_in_fail())[0][0]})
    page_data.update({'HistorySpendTime': round((db.read(Sql.tasks_get_spend_time())[0][0] / 60), 2)})
    page_data.update({'FailTaskCount': db.read(Sql.tasks_get_count_in_fail())[0][0]})

    return render_template('index.html', Data=page_data)


@app.route('/tasks/<page>', methods=['GET'])
def tasks(page):
    """
    任务
    """
    page = int(page)
    page_data = {}

    page_data.update({'PageName': 'Tasks'})
    page_data.update({'TaskList': db.read(Sql.tasks_get_all_item({'page': page}))})

    all_page = math.ceil(db.read(Sql.tasks_get_count())[0][0] / 10)
    next_page = page + 1 if page < all_page else page
    base_page = page - 1 if page > 1 else 1

    page_data.update({'CurrentPage': page})
    page_data.update({'AllPage': all_page})
    page_data.update({'NextPage': next_page})
    page_data.update({'BasePage': base_page})

    return render_template('tasks.html', Data=page_data)


@app.route('/cases/<tid>', methods=['GET'])
def cases(tid):
    """
    用例
    """
    page_data = {}
    page_data.update({'PageName': 'Cases'})

    # 转换用例格式
    base_case_list = db.read(Sql.cases_get_all_item({'tid': tid}))
    new_case_list = []
    for case_ in base_case_list:
        new_case_info = []
        number = 0
        for c_i in case_:
            if number == 9:
                c_i = c_i.split('\n')
            new_case_info.append(c_i)
            number += 1
        new_case_list.append(new_case_info)
    page_data.update({'CaseList': new_case_list})

    return render_template('cases.html', Data=page_data)
