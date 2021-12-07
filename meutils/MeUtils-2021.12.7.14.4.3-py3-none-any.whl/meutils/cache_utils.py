#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : cache_utils
# @Time         : 2021/11/24 上午11:09
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : https://cachetools.readthedocs.io/en/stable/
"""
FIFO：First In、First Out，就是先进先出。

LFU：Least Frequently Used，就是淘汰最不常用的。

LRU：Least Recently Used，就是淘汰最久不用的。

MRU：Most Recently Used，与 LRU 相反，淘汰最近用的。

RR：Random Replacement，就是随机替换。

TTL：time-to-live 的简称，也就是说，Cache 中的每个元素都是有过期时间的，如果超过了这个时间，那这个元素就会被自动销毁。
如果都没过期并且 Cache 已经满了的话，那就会采用 LRU 置换算法来替换掉最久不用的，以此来保证数量。
"""

from cachetools import cached, cachedmethod, LRUCache, RRCache, cachedmethod, TTLCache

def ttl_cache(ttl=60, maxsize=1024):
    """https://cachetools.readthedocs.io/en/stable/
    支持类对象缓存
    """
    return cached(TTLCache(maxsize, ttl))

# todo 支持 字典、列表、集合
