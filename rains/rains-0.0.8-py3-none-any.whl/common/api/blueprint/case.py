# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""

from flask import Blueprint

case = Blueprint('case', __name__)


@case.route('/case/cases', methods=['POST'])
def cases():
    """
    获取任务页面数据
    """
    try:
        return_data = {}
        tid = int(get_request_parameters('tid')['tid'])
        new_case_list = []
        base_case_list = db.read(Sql.cases_get_all_item({'tid': tid}))

        for case_ in base_case_list:
            new_case_info = []
            number = 0
            for c_i in case_:
                if number == 9:
                    c_i = c_i.split('\n')
                new_case_info.append(c_i)
                number += 1
            new_case_list.append(new_case_info)
        return_data.update({'cases': new_case_list})

        return successful(paras=return_data)

    except BaseException as e:
        return unsuccessful(f'{ e }')
