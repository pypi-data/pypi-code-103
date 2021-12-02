# Used for micro-service which developed by dapr
# install dapr before use
from fastapi import Header, HTTPException
from wisdoms.dapr import dapr_invoke
"""
    Example::

        from wisdoms.auth import permit

        host = {'AMQP_URI': "amqp://guest:guest@localhost"}

        auth = permit(host)

        class A:
            @auth
            def func():
                pass
"""
from nameko.rpc import rpc
from nameko.standalone.rpc import ServiceRpcProxy
from nameko.exceptions import RpcTimeout, MethodNotFound

import json
import traceback

from functools import wraps
from operator import methodcaller

from wisdoms.utils import xpt_func
from wisdoms.exec import UserException, WisdomErrorException
from wisdoms.commons import revert, codes

default_host = {'AMQP_URI': 'pyamqp://guest:guest@localhost'}
default_base_service = 'baseUserApp'


def rpc_with_timeout(host, service, func, data=None, timeout=8):
    try:
        with ServiceRpcProxy(service, host, timeout=timeout) as proxy:
            if data is not None:
                res = methodcaller(func, data)(proxy)
            else:
                res = methodcaller(func)(proxy)
            return res
    except RpcTimeout as e:
        print(service, ' ~~连接超时 %s sec......，检查是否启动......' % e)
        return revert(codes.TIMEOUT, desc=service + ' 连接超时')
    except MethodNotFound as e:
        print('function of this server %s not found,未找到方法 %s ' % (service, e))
        return revert(codes.GET_WAY_ERROR, desc='未找到方法' + e)


def rpc_wrapper(service_, func_, *args, host_=default_host, timeout_=8, **kwargs):
    """
    rpc包装方法

    :param service_:
    :param func_:
    :param host_:
    :param timeout_:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        with ServiceRpcProxy(service_, host_, timeout=timeout_) as proxy:
            res = methodcaller(func_, *args, **kwargs)(proxy)
            return res
    except RpcTimeout as e:
        print(service_, ' ~~连接超时 %s sec......，检查是否启动......' % e)
        return revert(codes.TIMEOUT, desc=service_ + ' 连接超时')
    except MethodNotFound as e:
        print('function of this server %s not found,未找到方法 %s ' % (service_, e))
        return revert(codes.GET_WAY_ERROR, desc='未找到方法' + e)


def ms_base(ms_host=None, base_service=None, func=None, **extra):
    """
    返回父类，闭包，传参数ms host
    :param ms_host:
    :param base_service
    :param func
    :param extra: 额外信息
    :extra: roles 角色权限
    :extra: name 微服务名称
    :extra: types 微服务类型 essential 类型的应用 角色必须带creator
    :extra: entrance 微服务pc入口
    :extra: entrance4app 小程序入口
    :extra: entrance4back 后台入口
    :extra: identity 唯一标识 暂时只用于平台base service 其他微服务不添加
    :return: class of base
    """

    ms_host = ms_host if ms_host else default_host
    base_service = base_service if base_service else default_base_service
    func = func if func else 'app2db'

    class MsBase:
        name = 'ms-base'

        @rpc
        # @exception()
        def export_info2db(self):
            """
            export information of this service to database

            :return:
            """
            clazz = type(self)
            service = clazz.name
            functions = dir(clazz)

            origin = extra
            origin['service'] = service
            origin['functions'] = functions

            rpc_with_timeout(ms_host, base_service, func, origin)

    return MsBase


def add_uid(app_id="base_app", method="/base/get_uid"):
    """
    验证用户token并且返回用户id
    :return: dict
    """
    def uid_(token=Header(alias="x-token", default=None)):
        if token == None or token == '':
            raise HTTPException(status_code=200,detail='未填写token信息')
        userInfo = dapr_invoke(app_id, method, {'token': token}).json()
        if userInfo['code'] ==1:
            return userInfo['data']
        else:
            raise HTTPException(status_code=200,detail=userInfo['desc'])
    return uid_


def add_user(app_id="base_app", method="/base/get_user"):
    """
    验证用户token并返回用户信息
    :extra: app_id 基础应用微服务名称
    :extra: method 获取用户信息方法名称
    :return: dict
    """
    def user_(token=Header(alias="x-token", default=None)):
        if token == None or token == '':
            raise HTTPException(status_code=200, detail='未填写token信息')
        userInfo = dapr_invoke(app_id, method, {'token': token}).json()
        if userInfo['code'] == 1:
            return userInfo['data']
        else:
            raise HTTPException(status_code=200, detail=userInfo['desc'])
    return user_
