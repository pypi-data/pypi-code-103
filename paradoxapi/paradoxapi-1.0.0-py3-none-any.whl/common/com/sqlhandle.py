#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:HDD

import sys, os

path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

import pymysql
from setting import *

class HandleMysql(object):
    def __init__(self, host, user, pwd, port, db):
        self.host = setting_try(host)
        self.port = port
        self.user = setting_try(user)
        self.pwd = setting_try(pwd)
        self.db = db
        self.charset = 'utf8'
        self.conn = self.connect_db()
        # 获取浮标
        self.cur = self.conn.cursor()

    def connect_db(self):
        # 连接数据库
        connect = pymysql.connect(host=self.host,
                                  user=self.user,
                                  password=self.pwd,
                                  port=self.port,
                                  db=self.db)
        return connect

    def read_db(self, sql):
        # 读取数据库
        try:
            self.cur.execute(sql)
            res = self.cur.fetchall()
            return res
        except Exception as exp:
            print('执行查询语句, 抛异常:{}'.format(exp))
            self.conn.close()
            return []
        #finally:
            #
