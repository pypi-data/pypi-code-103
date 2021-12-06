# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from rains.api.common import *


# 用例接口蓝图
case_blueprint = Blueprint('case', __name__)


@case_blueprint.route('/case/cases', methods=['POST'])
def cases() -> Response:
    """
    [ 获取用例信息列表 ]
    * 无

    [ 必要参数 ]
    * tid (int) : 所属任务ID

    [ 可选参数 ]
    * state (str) : 状态
    * page (int) : 页数
    * number (int) : 查询数量

    [ 返回内容 ]
    * (Response) : 指定 tid 任务的所有用例信息列表

    """

    try:
        # 获取请求参数
        api_paras = ServerParameter.analysis_request_paras('tid', 'state', 'page', 'number')
        # 获取服务器数据
        base_case_list = DB.read(SQL.case.get_info_from_tid(api_paras))

        # 加工数据
        # 将用例信息中的运行步骤转换成列表然后重新拼接数据
        new_case_list = []
        for case_info in base_case_list:
            new_case_info = []
            number = 0
            for info in case_info:
                if number == 9:
                    info = info.split('\n')
                new_case_info.append(info)
                number += 1
            new_case_list.append(new_case_info)
        return ServerParameter.successful({'cases': new_case_list})

    except BaseException as e:
        return ServerParameter.unsuccessful(f'{ e }')
