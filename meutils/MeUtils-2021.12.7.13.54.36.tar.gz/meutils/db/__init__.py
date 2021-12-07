#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : __init__.py
# @Time         : 2020/11/26 2:57 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :
from meutils.pipe import *


class DB(object):

    def __init__(self, is_test=None):

        if is_test is None:
            if HOST_NAME.__contains__('local') or LOCAL:
                is_test = True

        self.is_test = is_test

    def redis(self, ips=None, password=None):  # redis集群
        if self.is_test:
            return {}

        from rediscluster import RedisCluster

        startup_nodes = [dict(zip(['host', 'port'], ip.split(':'))) for ip in ips]

        rc = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            skip_full_coverage_check=True,
            password=password,
        )
        return rc

    def mysql(self, host='29.69.112.01'[::-1], port=3306, user='db_ai', passwd='db_Ai2019', db='ai'):
        import pymysql
        return pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)

    def mongodb(self):
        pass

    def hive(self):
        pass
