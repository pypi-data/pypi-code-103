# -*-coding:utf-8 -*-

import psycopg2
from psycopg2 import OperationalError
import datetime
import pandas as pd
import numpy as np
import os
import json
from datacenter_datasdk.verify import verify_args
import datacenter_datasdk.settings as settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class Postgres(object):

    def __init__(self, conf):
        try:
            self.database_postgres = psycopg2.connect(database=conf['database'],
                                                      user=conf['user'],
                                                      password=conf['password'],
                                                      host=conf['host'],
                                                      port=int(conf['port']))

            self.cursor = self.database_postgres.cursor()
        except OperationalError as e:
            raise e

    def find(self, table, filter_dict=None, columns=None):
        """
        查询所有满足条件的结果

        :param table: 表格名称
        :param filter_dict: 筛选字典
        :param columns: 返回字段
        :type table: str
        :type filter_dict: dict
        :type columns: list of str
        :return: 查询结果
        """
        if columns:
            columns_str = ",".join(['"{}"'.format(i) for i in columns])
        else:
            columns_str = '*'
        filter_list = []
        if not filter_dict:
            filter_dict = {}
        for k, v in filter_dict.items():
            if isinstance(v, str):
                v = "'{}'".format(v)
            elif isinstance(v, (datetime.datetime, datetime.date)):
                v = "'{}'".format(v)
            filter_list.append('"{}" = {}'.format(k, v))
        filter_str = 'where' + ' and '.join(filter_list) if filter_list else ''
        sql = "select {} from {} {}".format(columns_str, table, filter_str)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def find_by_sql(self, sql):
        """
        通过sql语句查询，返回所有结果
        :param sql: 查询语句
        :return:
        """
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def close_connect(self):
        """
        关闭数据库连接，查询、更新操作结束需要执行此操作
        """
        self.database_postgres.close()

    def get_column_name(self, table_name):
        sql = f"select column_name from information_schema.columns where table_name='{table_name}' and table_schema='public';"
        res = self.find_by_sql(sql)
        return [i[0] for i in res]


@verify_args(
    check={
        'region': str,
        'start_date': (datetime.datetime, datetime.date, str),
        'end_date': (datetime.datetime, datetime.date, str),
        'count': int,
        'source': str
    }
)
def get_trade_days(region, start_date=None, end_date=None, count=None, source=None):
    if not settings.pg_static:
        raise Exception('auth failed')
    if region == 'cn':
        source = source or 'jq'
    else:
        source = source or 'common'
    p = Postgres(settings.pg_static)
    if start_date:
        start_date = str(start_date)[:11]
    if end_date:
        end_date = str(end_date)[:11]
    if start_date:
        if end_date:
            if count:
                date_sql = f'"date" between \'{start_date}\' and  \'{end_date}\''
                sort_sql = f'order by "date" limit {count}'
            else:
                date_sql = f'"date" between \'{start_date}\' and  \'{end_date}\''
                sort_sql = ''
        else:
            if count:
                date_sql = f'"date" >= \'{start_date}\''
                sort_sql = f'order by "date" limit {count}'
            else:
                date_sql = f'"date" >= \'{start_date}\''
                sort_sql = f''
    else:
        if end_date:
            if count:
                date_sql = f'"date" <= \'{end_date}\''
                sort_sql = f'order by "date" desc limit {count}'
            else:
                date_sql = f'"date" <= \'{end_date}\''
                sort_sql = f''
        else:
            if count:
                date_sql = f''
                sort_sql = f'order by "date" limit {count}'
            else:
                date_sql = f''
                sort_sql = f''
    if not date_sql:
        sql = f'select "date" from {region}_{source}_trade_days {sort_sql};'
    else:
        sql = f'select "date" from {region}_{source}_trade_days where {date_sql} {sort_sql};'
    res = p.find_by_sql(sql=sql)
    p.close_connect()
    res_date = [i[0] for i in res]
    res_date.sort()
    return res_date


@verify_args(
    check={
        'region': str,
        'types': list,
        'code': str,
        'date': (datetime.datetime, datetime.date, str),
        'source': str
    }
)
def get_security_info(region, types=None, code=None, date=None, source=None):
    if not settings.pg_static:
        raise Exception('auth failed')
    if region == 'cn':
        source = source or 'jq'
    else:
        source =  source or 'common'
    if not types:
        types = ['etf', 'index', 'stock']
    if len(types) == 1:
        type_sql = f'"type"={repr(types[0])}'
    else:
        type_sql = f'("type" in {tuple(types)})' 
    p = Postgres(settings.pg_static)
    table_name = f"{region}_{source}_codes"
    columns = p.get_column_name(table_name)
    if not date:
        if not code:
            sql = f'select * from {table_name} where {type_sql};'

        else:
            sql = f'select * from {table_name} where code=\'{code}\' and {type_sql};'
    else:
        date = str(date)[:11]
        if not code:
            sql = f'select * from {table_name} where end_date>\'{str(date)}\' and {type_sql};'

        else:
            sql = f'select * from {table_name} where code=\'{code}\' and end_date>\'{str(date)}\' and {type_sql};'
    res = p.find_by_sql(sql=sql)
    df = pd.DataFrame(res, columns=columns)
    return df


def query(*args, **kwargs):
    # 初始化数据库链接
    engine = create_engine(
        f'postgresql+psycopg2://{settings.pg_static["user"]}:{settings.pg_static["password"]}@{settings.pg_static["host"]}:{settings.pg_static["port"]}/{settings.pg_static["database"]}')
    # 创建DBSession类型
    DBSession = sessionmaker(bind=engine)

    session = DBSession()
    query = session.query(*args, **kwargs)
    session.close()
    return query


@verify_args(
    check={
        'table_name': str,
        'condition': str
    }
)
def query_by_sql(table_name, condition=None, columns=None):
    p = Postgres(settings.pg_static)
    if not columns:
        columns = p.get_column_name(table_name)
    columns_f = [f'\"{i}\"' for i in columns]
    if condition:
        if '\"date\"' in condition:
            pass
        elif '\'date\'' in condition:
            condition = condition.replace('\'date\'', '"date"')
        elif 'date' in condition:
            condition = condition.replace('date', '\"date\"')
        else:
            pass
        sql = f'select {", ".join(columns_f)} from "{table_name}" where {condition} order by "date" limit 1000000;'
    else:
        sql = f'select {", ".join(columns_f)} from "{table_name}" order by "date" limit 1000000;'
    print(sql)
    res = p.find_by_sql(sql=sql)
    df = pd.DataFrame(res, columns=columns)
    return df