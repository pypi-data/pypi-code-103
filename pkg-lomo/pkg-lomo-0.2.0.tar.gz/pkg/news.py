# -*- coding: utf-8 -*-

# @File  : news.py
# @Author: Lomo
# @Site  : lomo.space
# @Date  : 2021-11-20
# @Desc  : crawler new demo
# URL : https://www.kancloud.cn/lizhixuan/free_api

import requests


class ChinaNews(object):
    def __init__(self):
        self.net_ease_url = 'https://api.apiopen.top/getWangYiNews'

    def get_net_news(self, page, count):
        req = requests.post(self.net_ease_url, {
            "page": page,
            "count": count
        })
        if req.status_code == 200:
            # print(req.json())
            rep = req.json()
            print(rep)
            return rep.get('result')


if __name__ == '__main__':
    r = ChinaNews().get_net_news(page=1, count=10)
    print(len(r))
