#!/usr/local/bin/python
# coding:utf-8
import sys, os
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)
from sqlhandle import *
import pandas as pd
from datacommon import *
from tips_data_common import *
env = 'pro'
# init_her_db
pld_her_db = HandleMysql(**get_db(env))
# init_wind_db
init_wind_db = plddb = HandleMysql(**get_db(env=env, db='wind'))

def merge_sql_str(code_list, tb_name, start, end, fields):
    # 拼接sql_str
    a_field, dt_string = her_annual_tb_fields_handle(start, end, fields)
    _sql_ = "select {} from hermes.{} where TICKER in ('{}') {}".format(a_field, tb_name,
                                                                        "','".join(code_list),
                                                                        dt_string)
    return _sql_

def her_annual_tb_fields_handle(start, end, fields):
    #
    a_fields = '*' if fields is None else ','.join(fields)
    start_str = "and PERIOD_DATE > '{}'".format(start) if start is not None else ''
    end_str = "and PERIOD_DATE < '{}'".format(end) if end is not None else ''
    dt_str = start_str + end_str
    return a_fields, dt_str

def get_her_data(sql, cols):
    # 读取Hermes的数据
    df = get_pld_any_data(pld_her_db, sql, cols)
    return df

def get_pld_any_data(db, sql, cols):
    # 统一get数据
    try:
        data = db.read_db(sql)
        df = pd.DataFrame(data, columns=cols)
        try:
            df = df.drop(['ID', 'UPDATE_TIME'], axis=1)
        except:
            pass
        return df
    except Exception as exp:
        print('读取数据抛异常:{}'.format(exp))
        return pd.DataFrame()