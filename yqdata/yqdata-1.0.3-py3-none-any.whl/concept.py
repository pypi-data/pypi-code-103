# -*- coding: UTF-8 -*-
# Author: Hu Min
# Date: 2021-11-30
import pandas as pd
from pandas import json_normalize
import logging
import logging.config
from utils.opensearch import get_client

def concept_list(src = 'ts'):
    """获取概念股分类，目前只有ts一个来源
    :param src:
    """
    logging.debug("get concept list")
    return get_client().search(index='concept', body={"size":1000000,"query":{"bool":{"must":[{"match":{"src":src}}],"must_not":[],"should":[]}}})

def concept_detail(id=None, ts_code=None):
    """获取概念股分类明细数据
    :param src:
    """
    logging.debug("get concept detail, id: %s, ts_code: %s" % (id, ts_code))
    if ts_code is None and id is not None:
        return get_client().search(index='concept_detail', body={"size":1000000,"query":{"bool":{"must":[{"match":{"id":id}}],"must_not":[],"should":[]}}})
    if id is None and ts_code is not None:
        return get_client().search(index='concept_detail', body={"size":1000000,"query":{"bool":{"must":[{"match":{"ts_code.keyword":ts_code}}],"must_not":[],"should":[]}}})
    return None

if __name__ == '__main__':
    print(concept_list('ts'))
