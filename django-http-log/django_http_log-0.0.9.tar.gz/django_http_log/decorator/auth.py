#!/user/bin/env python3
# -*- coding: utf-8 -*-
"""
--------------------------------------
    Author:     JiChao_Song
    Date  :     2021/11/28 下午6:48
    Desc  :
--------------------------------------
"""
from functools import wraps

from django_http_log.common.response import CommonResponse, CommonResultEnums, ParamsErrorResponse


def isAuthentication(flag=True):
    def view_decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            token = request.headers.get('Accesstoken')
            appId = request.headers.get('AppId')
            if verify_jwt(token) is None and flag:
                return CommonResponse(codeEnums = CommonResultEnums.TOKEN_INVAILD)
            return func(request, *args, **kwargs)

        return wrapper

    return view_decorator


def check_param(paramsList: list, method: list = None, ):
    """
    @author: sjch
    @desc: 检验必填阐述
    @method: 方法列表["POST", "GET"]
    @paramsList: 参数列表
    """

    if method is None:
        method = ['POST']

    def view_decorator(func):

        @wraps(func)
        def wrapper(request, *args, **kwargs):

            not_list = []
            if request.method == 'GET' and request.method in method:
                form = request.GET.copy()
            elif request.method == 'POST' and request.method in method:
                form = request.data.copy()
            else:
                return ParamsErrorResponse(message = f"只允许{','.join([str(i) for i in method])}请求", code = 40003)
            for i in paramsList:
                if i not in list(request.data.keys()):
                    not_list.append(i)
                else:
                    if form.get(i) == '' or form.get(i) is None:
                        return ParamsErrorResponse(message = f"{i}不能为空")
            if len(not_list) != 0:
                return ParamsErrorResponse(message = f"{','.join([str(i) for i in not_list])}" + "不能为空")

            return func(request, *args, **kwargs)

        return wrapper

    return view_decorator
