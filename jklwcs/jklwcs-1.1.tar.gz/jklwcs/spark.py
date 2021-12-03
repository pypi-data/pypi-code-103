# -*- coding: utf-8 -*-
'''
@File  : spark.py
@Author: Jike Data Analysis Modeling Group
@Date  : 2021/12/4 12:13 上午
@Desc  : spark 实例
'''

from pyspark.sql import SparkSession

try:
    spark_1 = SparkSession \
        .builder \
        .master("yarn") \
        .appName('user point data merge') \
        .config("spark.executor.memory", "40G") \
        .config("spark.executor.cores", "10") \
        .config("spark.executor.instances", "25") \
        .config("spark.driver.maxResultSize", "0") \
        .config("spark.spark.default.parallelism", "600") \
        .config("spark.storage.memoryFraction", "0.5") \
        .config("spark.shuffle.memoryFraction", "0.5") \
        .config("spark.shuffle.consolidateFiles", "true") \
        .config("spark.sql.broadcastTimeout", "-1") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.dynamicAllocation.enabled", "true") \
        .config("spark.dynamicAllocation.minExecutors", "15") \
        .config("spark.dynamicAllocation.maxExecutors", "25") \
        .config("spark.sql.adaptive.maxNumPostShufflePartitions", "1000") \
        .config("spark.sql.shuffle.partitions", "600") \
        .config("spark.sql.autoBroadcastJoinThreshold", "104857600") \
        .enableHiveSupport() \
        .getOrCreate()
except Exception as e:
    raise ConnectionError(f'spark connection error ...,{e}')


try:
    spark_2 = SparkSession \
        .builder \
        .master("yarn") \
        .appName('user point data merge') \
        .config("spark.executor.memory", "8G") \
        .config("spark.executor.cores", "5") \
        .config("spark.executor.instances", "30") \
        .config("spark.driver.maxResultSize", "0") \
        .config("spark.spark.default.parallelism", "600") \
        .config("spark.storage.memoryFraction", "0.5") \
        .config("spark.shuffle.memoryFraction", "0.5") \
        .config("spark.shuffle.consolidateFiles", "true") \
        .config("spark.sql.broadcastTimeout", "-1") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.dynamicAllocation.enabled", "true") \
        .config("spark.dynamicAllocation.minExecutors", "15") \
        .config("spark.dynamicAllocation.maxExecutors", "40") \
        .config("spark.sql.adaptive.maxNumPostShufflePartitions", "1000") \
        .config("spark.sql.shuffle.partitions", "600") \
        .config("spark.sql.autoBroadcastJoinThreshold", "104857600") \
        .enableHiveSupport() \
        .getOrCreate()
except Exception as e:
    raise ConnectionError(f'spark connection error ...,{e}')

