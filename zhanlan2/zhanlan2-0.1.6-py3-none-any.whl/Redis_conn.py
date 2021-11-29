#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/2 17:43
# @Author  : Adyan
# @File    : Redis_conn.py
import json

import redis

from datetime import datetime


class ReidsClient(object):

    def __init__(self, **kwargs):
        """
        :param kwargs: {
            "HOST": "119.29.9.92",
            "PORT": 6379,
            "DB": 11,
            "NAME":'proxy'
            }
        """
        host = kwargs.get('HOST', 'localhost')
        port = kwargs.get('PORT', 6379)
        password = kwargs.get('PAW', None)
        db = kwargs.get('DB', 0)
        NAME = kwargs.get('NAME', None)
        if password:
            self.redis_conn = redis.Redis(host=host, port=port, password=password)
        else:
            self.redis_conn = redis.Redis(host=host, port=port, db=db)
        self.NAME = NAME

    def get(self, count):
        lst = self.redis_conn.lrange(self.NAME, 0, count - 1)
        self.redis_conn.ltrim(self.NAME, count, -1)
        return lst

    def put(self, param):
        self.redis_conn.rpush(self.NAME, param)

    @property
    def queue_len(self):
        return self.redis_conn.llen(self.NAME)

    def prox(self):
        ip_list = []
        data_list = self.redis_conn.hgetall("proxy")
        for ip_item in data_list:
            proxy_expire_time = int(data_list[ip_item].decode())
            now_time = int(datetime.now().timestamp())
            time_dif = proxy_expire_time - now_time
            if time_dif < 10:
                print(ip_item.decode(), "过期 删除这个代理")
                self.redis_conn.hdel('proxy', ip_item)
            else:
                ip_list.append(ip_item.decode())
        return ip_list

