# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


import requests

from flask import Flask
from flask import render_template

from rains.api.blueprint.data import data_blueprint
from rains.api.blueprint.task import task_blueprint
from rains.api.blueprint.case import case_blueprint


app = Flask(__name__)
app.register_blueprint(data_blueprint)
app.register_blueprint(task_blueprint)
app.register_blueprint(case_blueprint)
app.config['JSON_AS_ASCII'] = False
app._static_folder = './static'


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    """
    首页
    """
    r = requests.get(''.join([request.host_url, 'data/summarize'])).json()
    return _return_page(r, 'index.html')


@app.route('/task/<page>', methods=['GET'])
def task(page):
    """
    任务
    """
    r = requests.post(''.join([request.host_url, 'task/tasks']), data={'page': page}).json()
    return _return_page(r, 'task.html')


@app.route('/case/<tid>', methods=['GET'])
def case(tid):
    """
    用例
    """
    r = requests.post(''.join([request.host_url, 'case/cases']), data={'tid': tid}).json()
    return _return_page(r, 'case.html')


@app.errorhandler(404)
def error_404(error):
    print(error)
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_500(error):
    print(error)
    return render_template('500.html'), 500


def _return_page(return_data, html_name):
    if return_data['code'] == 200:
        return render_template(html_name, Data=return_data['data'])
    else:
        return render_template('500.html'), 500
