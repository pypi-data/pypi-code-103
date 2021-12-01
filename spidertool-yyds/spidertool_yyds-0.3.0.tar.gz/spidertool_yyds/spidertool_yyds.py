# -*- coding: utf-8 -*-
# __author__ = "Casey"  395280963@qq.com
# Date: 2021-12-01  Python:3.6

import datetime
# import time


def yesterday_time():
    yesterday = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    return yesterday
