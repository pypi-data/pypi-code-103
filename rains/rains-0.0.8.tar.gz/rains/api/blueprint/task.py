# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


import math

from rains.api.common import *


# 任务接口蓝图
task_blueprint = Blueprint('task', __name__)


@task_blueprint.route('/task/tasks', methods=['POST'])
def tasks() -> Response:
    """
    [ 获取任务信息列表 ]
    * 无

    [ 必要参数 ]
    * 无

    [ 可选参数 ]
    * page (int): 页数
    * number (int): 查询数量

    [ 返回内容 ]
    * (Response) : 任务信息列表

    """

    try:
        # 获取请求参数
        api_paras = ServerParameter.analysis_request_paras('page', 'number')
        # 获取服务器数据
        task_list = DB.read(SQL.task.get_info_all(api_paras))
        task_all_count = DB.read(SQL.task.get_count_all())[0][0]

        # 加工数据
        return_data = {'tasks': task_list}
        page = 1 if 'page' not in api_paras.keys() else int(api_paras['page'])
        number = 10 if 'number' not in api_paras.keys() else int(api_paras['number'])
        return_data.update({'current_page': page})
        # 获取所有的页面
        all_page = math.ceil(task_all_count / number)
        return_data.update({'all_page': all_page})
        return_data.update({'next_page': page + 1 if page < all_page else page})
        return_data.update({'back_page': page - 1 if page > 1 else 1})

        return ServerParameter.successful(return_data)

    except BaseException as e:
        return ServerParameter.unsuccessful(f'{ e }')
