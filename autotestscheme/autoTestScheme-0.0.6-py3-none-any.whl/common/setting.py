# -*- coding: utf-8 -*-
#!/usr/bin/env python
__owner__ = "熊润"
__created_date__ = "2019/9/23"

from .common import NewDict

"""

Usage:
    配置读取

"""

from . import constant, logger, start_data
from . import config


class ConfigureObj1(object):
    pass


class Payment(object):

    __species = None

    def __new__(cls, *args, **kwargs):
        if not cls.__species:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self):
        self.config_obj = config.Json(constant.CONFIG_PATH)
        self.robot = self.get_robot_configure()
        self.payment = self.get_payment_configure()

    def get_payment_configure(self):
        class ConfigureObj1(object):
            pass
        payment = self.config_obj.get('payment')
        _config = NewDict(payment.get('base'))
        _config.merge(payment.get(start_data.TEST_ENV))

        if start_data.TEST_ENV in list(payment.keys()):
            obj = ConfigureObj1()
            obj.env = start_data.TEST_ENV
            obj.base_url = _config.get('base_url')
            obj.secret = _config.get('secret')
            obj.base_url = _config.get('base_url')
            obj.secret = _config.get('secret')
            response = self.get_disconf(_config.get('disconf'))
            # print('----------------------------payment', _config)
            sql = {}
            if not constant.IS_JENKINS:
                character = 'default'
            else:
                character = 'jenkins'
            obj.isvId = response.get('ceres.gate.jdbc.isvId')
            if _config.get('isvId') is not None:
                obj.isvId = _config.get('isvId')
            sql['host'] = response.get('ceres.gate.jdbc.{}.host'.format(character))
            sql['port'] = int(response.get('ceres.gate.jdbc.{}.port'.format(character)))
            sql['user'] = response.get('ceres.gate.jdbc.{}.username'.format(character))
            sql['passwd'] = response.get('ceres.gate.jdbc.{}.password'.format(character))
            sql['db'] = response.get('ceres.gate.jdbc.{}.database'.format(character))
            obj.sql = sql
            return obj
        logger.error('{}测试环境配置不存在'.format(start_data.TEST_ENV))

    def get_robot_configure(self):
        obj = ConfigureObj1()
        obj.type = self.config_obj.get('robot').get('type')
        obj.link = self.config_obj.get('robot').get('link')
        obj.title = self.config_obj.get('robot').get('title')
        obj.is_at_all = self.config_obj.get('robot').get('is_at_all')
        obj.configure = self.config_obj.get('robot').get(obj.type)
        obj.access_token = obj.configure.get('access_token')
        obj.secret = obj.configure.get('secret')
        obj.at_list = obj.configure.get('at_list')
        return obj



# _setting = Payment()
# robot = _setting.robot
# payment = _setting.payment
