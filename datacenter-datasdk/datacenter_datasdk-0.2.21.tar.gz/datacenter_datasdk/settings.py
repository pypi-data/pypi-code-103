# -*-coding:utf-8 -*-
import json
import numpy as np
import os
from datacenter_datasdk.verify import crypt
import base64

td_type_map = {
    1: np.bool_,
    2: np.int8,
    3: np.int16,
    4: np.int32,
    5: np.int64,
    6: np.float_,
    7: np.double,
    8: np.string_,
    9: 'datetime64[ns]',
    10: np.string_
}

td_token = ''
td_url= ''
pg_static = {}


def auth(encrypted, key):
    global td_token, td_url, pg_static     
    try:
        b_encrypted = bytes(encrypted, encoding='utf-8')  
        source_str = crypt(str(base64.b64decode(b_encrypted), 'utf-8'), key)
        source = json.loads(source_str)
    except:
        raise Exception('auth failed')
    td_token = source.get('td_token')
    td_url = source.get('td_url')
    pg_static = source.get('pg_static')
    if td_token and td_url and pg_static:
        print('auth success')

td_columns = {
    "cn_d1":  ["code", "time", "open", "close", "low", "high", "volume", "money",
               "factor", "high_limit", "low_limit", "avg", "pre_close",
               "paused", "update_date"],
    "cn_d1_post":  ["code", "time", "open", "close", "low", "high", "volume", "money",
               "factor", "high_limit", "low_limit", "avg", "pre_close",
               "paused", "update_date"],
    "cn_d1_raw":  ["code", "time", "open", "close", "low", "high", "volume", "money",
               "factor", "high_limit", "low_limit", "avg", "pre_close",
               "paused", "update_date"],
    "cn_m1": ["code", "time", "open", "close", "low", "high", "volume", "money",
              "factor", "high_limit", "low_limit", "avg", "pre_close",
              "paused", "update_date"],
    "cn_m5": ["code", "time", "open", "close", "low", "high", "volume", "money",
              "factor", "high_limit", "low_limit", "avg", "pre_close",
              "paused", "update_date"],
    "cn_m15": ["code", "time", "open", "close", "low", "high", "volume", "money",
               "factor", "high_limit", "low_limit", "avg", "pre_close",
               "paused", "update_date"],
    "cn_m30": ["code", "time", "open", "close", "low", "high", "volume", "money",
               "factor", "high_limit", "low_limit", "avg", "pre_close",
               "paused", "update_date"],
    "cn_m60": ["code", "time", "open", "close", "low", "high", "volume", "money",
               "factor", "high_limit", "low_limit", "avg", "pre_close",
               "paused", "update_date"],
    "cn_tick":  ["code",  "time",  "current",  "high",  "low",  "volume",  "money",
                 "a1_v", "a2_v", "a3_v", "a4_v", "a5_v", "a1_p", "a2_p",
                 "a3_p", "a4_p", "a5_p",  "b1_v",  "b2_v",  "b3_v",  "b4_v",  "b5_v",
                 "b1_p",  "b2_p",  "b3_p",  "b4_p",  "b5_p"],
    "us_d1": ["code", "time", "open", "high", "low", "close", "pre_close", "avg",
              "volume", "money", "unix_timestamp", "update_date"],
    "us_m1": ["code", "time", "open", "high", "low", "close", "pre_close", "avg",
              "volume", "money", "unix_timestamp", "update_date"],
    "us_m5": ["code", "time", "open", "high", "low", "close", "pre_close", "avg",
              "volume", "money", "unix_timestamp", "update_date"],
    "us_m15": ["code", "time", "open", "high", "low", "close", "pre_close", "avg",
               "volume", "money", "unix_timestamp", "update_date"],
    "us_m30": ["code", "time", "open", "high", "low", "close", "pre_close", "avg",
               "volume", "money", "unix_timestamp", "update_date"],
    "us_m60": ["code", "time", "open", "high", "low", "close", "pre_close", "avg",
               "volume", "money", "unix_timestamp", "update_date"]
}
