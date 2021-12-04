#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import traceback
import logging
import uuid
from datetime import datetime

logger = logging.getLogger('logger')
import threading
local_data = threading.local()

def set_thread_local_trac_id(func_name):
    local_data.trac_id = uuid.uuid1().hex
    return local_data.trac_id

def remove_thread_local_trac_id():
    return True


def add_all_dic(origin_dic, source_dic):
    for key in source_dic:
        origin_dic[key] = source_dic[key]
    return origin_dic

def info(message):
    try:
        logger.info(message)
    except Exception as e:
        print(e)


def warn(message):
    try:
        logger.warning(message)
    except Exception as e:
        print(e)


def error(message):
    try:
        logger.error(message)
    except Exception as e:
        print(e)



def list_to_dic(items, keys):
    if items is None:
        items = []
    if not isinstance(items, list):
        items = [items]
    res_dic = {}
    for item in items:
        dic_key = ''
        for key in keys:
            dic_key = dic_key + str(item[key]) + '_'
        res_dic[dic_key[:-1]] = item
    return res_dic

def get_data(retry_max_count, func, *args):
    data = None
    try:
        if retry_max_count > 0:
            data = func(*args)
    except Exception as e:
        error(traceback.format_exc())
        retry_max_count = retry_max_count - 1
        time.sleep(0.3)
        return get_data(retry_max_count, func, *args)
    return data

def check_trade_range_time(start_time_interval,end_time_interval,rainiee_client):
    from interval import Interval
    # 先判断当前时间是否在时间区间内
    # 当前时间
    now_localtime = time.strftime("%H:%M:%S", time.localtime())
    # 当前时间（以时间区间的方式表示）
    now_time = Interval(now_localtime, now_localtime)
    # 在当前时间区间内，在去判断当天是否为交易日
    if now_time in start_time_interval or now_time in end_time_interval:
        return check_trade_date(datetime.today().date(),rainiee_client)
    return False

def check_trade_date(date,rainiee_client):
    return rainiee_client.vip_channel().is_trading_day(date=date.strftime('%Y%m%d'))


def model_to_dict(models):
    from django.forms import model_to_dict
    return_list = []
    for model in models:
        return_list.append(model_to_dict(model, exclude=[]))
    return return_list