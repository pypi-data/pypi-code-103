# -*- coding: utf-8 -*-
'''
@File  : func.py
@Author: Jike Data Analysis Modeling Group
@Date  : 2021/12/4 12:13 上午
@Desc  : 功能函数
'''


import logging
import datetime

def get_logger(log_name):
    """ 定时器"""
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler = logging.FileHandler(
        filename=f"/mnt/disk1/data/jkdaae/logs/{log_name}_{datetime.datetime.today().date().isoformat()}.log",
        encoding='utf-8', mode='w')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger

def tran_business_hours(business_hours):
    """营业时间转换"""
    business_hours_list = []
    for business_hour in business_hours:
        hour_list = business_hour.split('_')
        s_hour = int(hour_list[0])
        e_hour = int(hour_list[1])
        if s_hour > e_hour:
            business_hours_list.extend(list(range(s_hour, 24)))
            business_hours_list.extend(list(range(0, e_hour + 1)))
        else:
            business_hours_list.extend(list(range(s_hour, e_hour + 1)))
    return business_hours_list