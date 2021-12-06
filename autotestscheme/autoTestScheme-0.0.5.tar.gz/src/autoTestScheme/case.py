import random
import time
import os
import sys
from decimal import Decimal
import json_tools
import allure
import pytest
from .common import start_data, config
from .common.bump import dict_value_hump2underline
from .common import logger
from .common.parse import Parse
from .common.common import NewDict
from .common.conversion import Conversion
from .common.sql import MySql
from .request import requestBase


class Base(Parse):

    logger = logger

    def setup_class(self):
        self.session = self.get_session()

    @classmethod
    def get_session(self):
        return requestBase()

    def get_mysql_client(self, database_kwargs):
        sql = MySql()
        sql.connect(database_kwargs)
        return sql

    def on_locust_start(self):
        """
        此函数用于兼容locust,locust用例的setup相当于on_start
        """
        self.session.session = self.client
        self.session.catch_response = True
        self.logger.error("------------123------------")
        self.logger.error(dir(self))
        if 'setup' in dir(self):
            self.setup()

    def set_test_env(self, env: str):
        """
        设置环境
        :param env:
        :return:
        """
        start_data.TEST_ENV = env

    def read_config(self, folder_name: str ='config'):
        """
        读取配置文件
        :param folder_name: 文件目录名，请将配置文件放置跟目录下
        :return:
        """
        config_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), folder_name, start_data.TEST_ENV + ".json")
        logger.debug(config_path)
        return config.Json(config_path)

    def get_unique_identification(self):
        """
        获取唯一标识，多线程可用，用于性能测试使用
        """
        return 'test{}_{}_{}'.format(''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', 4)),
                                              ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba', 4)),
                                              str(float(time.time())))

    @pytest.fixture()
    def data_conversion(self, request):
        '''
            数据转换使用,将数据进行特殊转换
        '''
        if 'data' in list(request.node.funcargs.keys()):
            param = request.node.funcargs.get('data')
            self.logger.error(param)
        else:
            param = request.getfixturevalue('data')
        param = self.conversion(param)
        if param != {}:
            logger.error(start_data.TAG_LIST)
            param['title'] = '{}_{}'.format(start_data.TAG_LIST[param['tag']], param['title'])
            allure.dynamic.title(param.get('title'))
            if param.get('story') is not None:
                allure.dynamic.story(param.get('story'))
            request.node.name = param.get('title')
        return param

    def get_func(self, func):
        if func in dir(self):
            return eval('self.{}'.format(func))
        return False

    def conversion(self, param, title=''):
        con = Conversion(self, param)
        con.re_dict()
        param = con.json
        self.excute_dynamic(param.get('issue'), 'issue')
        self.excute_dynamic(param.get('link'), 'link')
        self.excute_dynamic(param.get('testcase'), 'testcase')
        return self.get_my_dict(param)

    def get_my_dict(self, param):
        '''
        将字典类添加一个新的获取方法(gets)，改方法可以一次性获取多个值
        @param param: 字典类
        @return: MyDict类
        '''
        return NewDict(param)

    def check_response(self, response, outs):
        '''
            数据对比，常用于在判断请求结果与预期的校验
        '''
        compare = json_tools.diff(outs, response)
        result = {'remove':[], 'add':[], 'replace':[]}
        for i in compare:
            _type = ''
            if 'remove' in list(i.keys()):
                _type = 'remove'
                i = i['remove']
            elif 'add' in list(i.keys()):
                _type = 'add'
                i = i['add']
            elif 'replace' in list(i.keys()):
                _type = 'replace'
                i['新对象'] = i['value']
                i['原对象'] = i['prev']
                i['路径'] = i['replace']
                del i['value']
                del i['prev']
                del i['replace']
            result[_type].append(i)
        if len(result['add']) > 0:
            self.logger.warning('校验的内容中增加的字段:{}'.format(' ; '.join(result['add'])))
        msg = []
        if len(result['remove']) > 0:
            msg.append("校验的内容中被删除的字段:{}".format(' ; '.join(result['remove'])))
        if len(result['replace']) > 0:
            msg.append("校验的内容中被修改的字段及内容:{}".format(result['replace']))
        assert len(msg) == 0, '比较结果:{}'.format(';'.join([str(i) for i in msg]))

    def check_inclusion_relation(self, a, b):
        '''
            a,b都是dict类型
            判断b是否包含a内的所有元素
        '''
        for i in list(a.items()):
            if i not in list(b.items()):
                self.logger.error('不包含元素:{},数据:\na:{},\nb:{}'.format(i, a, b))
                return False
        return True

    def excute_dynamic(self, dynamic, name):
        dynamic_list = {}
        dynamic_list['issue'] = allure.dynamic.issue
        dynamic_list['link'] = allure.dynamic.link
        dynamic_list['testcase'] = allure.dynamic.testcase
        if dynamic is not None:
            if type(dynamic) == dict:
                for a, b in dynamic.items():
                    dynamic_list[name](b, a)
            elif type(dynamic)  == list:
                for i in dynamic:
                    if type(i) == list:
                        dynamic_list[name](*i)
                    dynamic_list[name](i)

    def check_response_by_sql(self, response, outs):
        '''
            比较返回与数据库，与check_response的区别在于会将response与outs的key转换为下划线形式字符串
        '''
        response = dict_value_hump2underline(response)
        outs = dict_value_hump2underline(outs)
        return self.check_response(response, outs)

    def conver_decimal(self, data:dict) -> dict:
        """
        将字典内的Decimal类型字段转换未float
        @param data:
        @return:
        """
        for i in list(data.keys()):
            if type(data[i]) == Decimal:
                data[i] = float(data[i])
        return data
