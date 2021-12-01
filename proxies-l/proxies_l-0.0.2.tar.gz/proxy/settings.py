#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/19 17:30
# @Author  : Adyan
# @File    : settings.py

from Utils import Headers

PROXY_NAME = 'proxies'
HOST = '47.107.86.234'
PORT = 6379
DB = 10
# redis的密码，如果没有不用配置
# PASSWORD = 'rootroot'

# 测试网站
TSET_API = 'https://www.baidu.com/'
# TSET_API = 'https://www.taobao.com/'
TEST_HEADERS = Headers().headers()
# 测试单个代理的超时时长
TEST_TIME_OUT = 10
# 循环校验事件
CYCLE_VAILD_TIME = 60
# 代理池数量的最小值配置
LOWER_THRESHOLD = 20
# 代理池数量的最大值配置
UPPER_THRESHOLD = 40
# 循环添加时间
ADD_CYCLE_TIME = 60
PROXY_OFF = "taiyang"
PROXY_API = {
    "jingling": {
        "name": "jingling_ip",
        "url": f'http://ip.ipjldl.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&groupid=0&qty=20&time=100&pro=&city=&port=1&format=json&ss=5&css=&ipport=1&dt=1&specialTxt=3&specialJson=&usertype=2',
        "add_whitelist": "http://www.jinglingdaili.com/Users-whiteIpAddNew.html?appid=13498&appkey=f3b53f02df1d5d94a2c16816b28846dc&type=dt&whiteip=%s&index=1",
    },
    "taiyang": {
        "name": "taiyang_ip",
        "url": "http://http.tiqu.alibabaapi.com/getip3?num=10&type=2&pack=74668&port=1&lb=1&pb=45&gm=4&regions=",
        "add_whitelist": 'http://ty-http-d.hamir.net/index/white/add?neek=tyhttp630285&appkey=7dde6c70c2217f9e17affae77eb9d490&white=%s'
    },

}
