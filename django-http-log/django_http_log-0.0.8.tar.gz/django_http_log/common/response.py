#!/user/bin/env python3
# -*- coding: utf-8 -*-
"""
--------------------------------------
    Author:     JiChao_Song
    Date  :     2021/11/28 15:31
    Desc  :
--------------------------------------
"""
import datetime

from django.http import JsonResponse


class AbstractBaseCodeMessageEnum:

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class CommonResultEnums:
    SUCCESS = AbstractBaseCodeMessageEnum(code = 20000, message = '请求成功')

    TOKEN_INVAILD = AbstractBaseCodeMessageEnum(code = 40001, message = 'token失效')

    SYSTEM_EXCEPTION = AbstractBaseCodeMessageEnum(code = 50000, message = '系统异常')


class CommonResponse:

    def __new__(cls, codeEnums: AbstractBaseCodeMessageEnum, result: any = None):
        return JsonResponse(
            data = dict(
                code = codeEnums.code,
                message = codeEnums.message,
                result = result,
                systemTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                type = 'success'
            ),
            json_dumps_params = {"ensure_ascii": False}
        )


class SuccessResponse:

    def __new__(cls, result: any, codeEnums: CommonResultEnums.SUCCESS):
        return JsonResponse(
            data = dict(
                code = codeEnums.code,
                message = codeEnums.message,
                result = result,
                systemTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                type = 'success'
            ),
            json_dumps_params = {"ensure_ascii": False}
        )


class SystemExceptionResponse:

    def __new__(cls, codeEnums: CommonResultEnums.SYSTEM_EXCEPTION, result: any = None):
        return JsonResponse(
            data = dict(
                code = codeEnums.code,
                message = codeEnums.message,
                result = result,
                systemTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                type = 'error'
            ),
            json_dumps_params = {"ensure_ascii": False}
        )


class ParamsErrorResponse:

    def __new__(cls, message: str, code=40002, result=None):
        return JsonResponse(
            data = dict(
                code = code,
                message = message,
                result = result,
                systemTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                type = 'success'
            ),
            json_dumps_params = {"ensure_ascii": False}
        )
