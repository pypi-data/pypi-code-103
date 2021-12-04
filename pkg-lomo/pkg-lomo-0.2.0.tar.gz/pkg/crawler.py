# -*- coding: utf-8 -*-

# @File  : crawler.py
# @Author: Lomo
# @Site  : lomo.space
# @Date  : 2021-11-20
# @Desc  : crawler demo
# URL : https://www.kancloud.cn/lizhixuan/free_api

import requests


class Crawler(object):
    def __init__(self):
        pass

    @staticmethod
    def is_ok(url):
        req = requests.get(url)
        print(req.status_code)
        if req.status_code == 200:
            return True
        else:
            return False

    @staticmethod
    def get_contents(url):
        req = requests.api.get(url)
        print(req.content)
        # print(req.json())

    @staticmethod
    def get_jokes(url=None, **params):
        url = url if url else 'https://api.apiopen.top/getJoke'
        page = params.get('page')
        count = params.get('count')
        _type = params.get('type')
        req_params = {'page': page, 'count': count, 'type': _type}
        req = requests.get(url, req_params)
        print(req.status_code)
        if len(req.json()['result']):
            print(len(req.json()['result']))
            return req.json()['result']
        else:
            return None

    @staticmethod
    def search_joke_by_sid(sid, url=None):
        # url = url if url else 'https://api.apiopen.top/getSingleJoke'
        # url = url + '?sid=' + sid
        if not url:
            url = 'https://api.apiopen.top/getSingleJoke'
        req = requests.get(url=url, params={'sid': sid})
        print(req.url)
        print(req.status_code)
        # print(req.json())
        return req.json()['result']


if __name__ == '__main__':
    # Crawler.get_contents(url='https://www.baidu.com/')
    # Crawler.is_ok('https://www.baidu.com/')
    print(Crawler.search_joke_by_sid(sid='31551566'))

    # params = {'page': 1, 'count': 5, 'type': 'all'}
    # print(Crawler.get_jokes(**params))
