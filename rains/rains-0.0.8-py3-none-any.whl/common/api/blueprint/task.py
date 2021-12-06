# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


import math

from flask import Blueprint

task = Blueprint('task', __name__)


@task.route('/task/tasks', methods=['POST'])
def tasks():
    """
    获取任务页面数据
    """
    try:
        return_data = {}
        page = int(get_request_parameters('page')['page'])
        all_page = math.ceil(db.read(Sql.tasks_get_count())[0][0] / 10)
        next_page = page + 1 if page < all_page else page
        back_page = page - 1 if page > 1 else 1

        return_data.update({'tasks': db.read(Sql.tasks_get_all_item({'page': page}))})
        return_data.update({'current_page': page})
        return_data.update({'all_page': all_page})
        return_data.update({'next_page': next_page})
        return_data.update({'back_page': back_page})

        return successful(paras=return_data)

    except BaseException as e:
        return unsuccessful(f'{ e }')
