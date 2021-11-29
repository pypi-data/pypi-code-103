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


class IpProxy:

    def __init__(self, count: int,url):
        self.count = count
        self.url = url

    def get_jingling(self):
        # url = f'http://ip.ipjldl.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&groupid=0&qty={self.count}&time=100&pro=&city=&port=1&format=json&ss=5&css=&ipport=1&dt=1&specialTxt=3&specialJson=&usertype=2'
        r = json.loads(requests.get(self.url).text)
        ip_list = []
        try:
            if '登' in r.get('msg'):
                res = re.findall('(.*?)登', r.get("msg"))
                add_ip_url = f"http://www.jinglingdaili.com/Users-whiteIpAddNew.html?appid=13498&appkey=f3b53f02df1d5d94a2c16816b28846dc&type=dt&whiteip={res[0]}&index=1"
                res = requests.get(add_ip_url, timeout=10)
                r = json.loads(requests.get(self.url).text)

            logging.info(r)
            for item in r["data"]:
                ip_list.append("https://" + item['IP'])
        except:
            logging.info(r)
        if ip_list:
            return ip_list

    def get_taiyang(self):
        pass

    def get_zhima(self):
        pass

    def get_proxy(self):
        pass


