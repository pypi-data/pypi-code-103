# -*- coding: utf-8 -*-
'''
@File  : conf.py
@Author: Jike Data Analysis Modeling Group
@Date  : 2021/12/4 1:22 下午
@Desc  : spark配置
'''

class JKSparkConf(object):

    _options = {}

    @classmethod
    def config(cls,key,value):
        cls._options[key] = value
        return cls

    @classmethod
    def get(cls):
        from jklwcs.select.uuid import  set_spark_conf
        for key, value in cls._options.items():
            set_spark_conf(key,value)



