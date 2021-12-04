# -*- coding: utf-8 -*-
'''
@File  : conf.py
@Author: Jike Data Analysis Modeling Group
@Date  : 2021/12/4 1:22 下午
@Desc  : spark配置
'''

from pyspark.sql import SparkSession

class JKSparkSession(object):

    _options = {}
    _spark = SparkSession \
        .builder \
        .master("yarn")\
        .enableHiveSupport()

    @classmethod
    def appName(cls,name):
        return cls._spark.appName(name)

    @classmethod
    def config(cls,key,value):
        cls._options[key] = value
        return cls

    @classmethod
    def get(cls):
        for key, value in cls._options.items():
            cls._spark.config(key,value)
        cls._spark.getOrCreate()
        return cls._spark


