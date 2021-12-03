#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/10 10:53
# @Author  : Adyan
# @File    : proxy.py


import json
import logging
import random
import re
import time
import requests
from datetime import datetime

cache = {}
limit_times = [10]


def stat_called_time(func):
    def _called_time(*args, **kwargs):
        key = func.__name__
        if key in cache.keys():
            cache[key][0] += 1
        else:
            call_times = 1
            cache[key] = [call_times, time.time()]
        if cache[key][0] <= limit_times[0]:
            res = func(*args, **kwargs)
            cache[key][1] = time.time()
            return res
        else:
            return None

    return _called_time


class ProxyMeta(type):
    def __new__(mcs, name, bases, attrs):
        attrs['__Crawl_Func__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__Crawl_Func__'].append(k)

        return type.__new__(mcs, name, bases, attrs)


class ProxyGetter(metaclass=ProxyMeta):
    """
    :sample code:
        ProxyGetter(
         url='Obtain the proxy IP address',
         name='The name of the method called',
         add_whitelist='Add a whitelist address'
         del_whitelist='The whitelist address is deleted'
     ).get_proxies()
    """

    def __init__(
            self, url, name,
            add_whitelist=None,
            del_whitelist=None
    ):
        self.url = url
        self.name = name
        self.add_whitelist = add_whitelist
        self.del_whitelist = del_whitelist

    def get_proxies(self):
        """
        通过方法名调用方法，获取代理
        :param callfunc:
        :return:
        """
        proxies = []
        try:
            res = eval(f'self.{self.name}()')
            if isinstance(res, dict):
                return res
            for proxy in res:
                proxies.append(proxy)
        except:
            pass
        if proxies:
            return proxies

    @stat_called_time
    def jingling_ip(self):
        ip_list = []
        res = json.loads(requests.get(self.url).text)
        if not res.get("data"):
            msg = res.get('msg')
            if "限制" in msg:
                time.sleep(random.randint(1, 3))
            if '登' in msg:
                limit_times[0] += 1
                _ip = re.findall('(.*?)登', res.get("msg"))
                requests.get(self.add_whitelist % _ip[0], timeout=10)
            res = json.loads(requests.get(self.url).text)

        logging.info(f"{str(datetime.now())[:-7]}-{res}")
        print(f"{str(datetime.now())[:-7]}-{res}")

        if res.get("data"):
            for item in res.get("data"):
                ip_list.append("https://" + item['IP'])

        if ip_list:
            return ip_list
        else:
            return res

    @stat_called_time
    def taiyang_ip(self):
        time.sleep(random.randint(2, 4))
        ip_list = []
        res = json.loads(requests.get(self.url).text)
        if not res.get("data"):
            msg = res.get("msg")
            if '请2秒后再试' in msg:
                limit_times[0] += 1
            if '请将' in msg:
                _ip = msg.split("设")[0][2:]
                print(requests.get(self.add_whitelist % _ip).text)
            if '当前IP' in msg:
                _ip = msg.split("：")[1]
                print(requests.get(self.add_whitelist % _ip).text)
            res = json.loads(requests.get(self.url).text)

        logging.info(f"{str(datetime.now())[:-7]}-{res}")
        print(f"{str(datetime.now())[:-7]}-{res}")

        if res.get("data"):
            for item in res.get("data"):
                ip_list.append(f"https://{item['ip']}:{item['port']}")

        if ip_list:
            return ip_list
        else:
            return res

    @stat_called_time
    def zhima_ip(self):
        pass

    @stat_called_time
    def source_proxy(self):
        res = json.loads(requests.get(self.url).text)
        if not res.get("data"):
            msg = res.get("msg")
            if '请2秒后再试' in msg:
                limit_times[0] += 1
                time.sleep(random.randint(2, 4))
            res = json.loads(requests.get(self.url).text)

        logging.info(f"{str(datetime.now())[:-7]}-{res}")
        print(f"{str(datetime.now())[:-7]}-{res}")

        if res.get("data"):
            return res.get("data")
        else:
            return res
