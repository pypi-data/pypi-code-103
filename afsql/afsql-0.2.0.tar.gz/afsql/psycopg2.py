# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     psycopg2
   Description :
   Author :        Asdil
   date：          2021/4/8
-------------------------------------------------
   Change Activity:
                   2021/4/8:
-------------------------------------------------
"""
__author__ = 'Asdil'
import psycopg2
from psycopg2 import pool


class Psycopg:
    """
    Psycopg类用于链接Psycopg
    """

    def __init__(self, host, port, user, password, database, minconn=2, maxconn=10):
        """__init__(self):方法用于

        Parameters
        ----------
        host : str
            host地址
        port : int
            端口
        user : str
            用户名
        password : str
            密码
        database : str
            数据库名称
        minconn : int
            最小连接数
        maxconn : int
            最大连接数

        Returns
        ----------
        """
        try:
            self.connectPool = pool.ThreadedConnectionPool(minconn, maxconn, host=host, port=port,
                                                           user=user, password=password,
                                                           database=database)

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)

    def get_connect(self):
        """getConnect方法用于生成新连接"""
        conn = self.connectPool.getconn()
        cursor = conn.cursor()
        return conn, cursor

    def close_connect(self, conn, cursor):
        """closeConnect方法用于关闭连接

        Parameters
        ----------
        cursor : object
            游标
        conn : object
            连接
        Returns
        ----------
        """
        cursor.close()
        self.connectPool.putconn(conn)

    def close_all(self):
        """close_all方法用于断开连接

        Parameters
        ----------
        param : str

        Returns
        ----------
        """
        self.connectPool.closeall()

    def select_one(self, sql, args=None):
        """select_one方法用于查找一条数据

        Parameters
        ----------
        sql : str
            查询语句
        args : list or None
            参数
        Returns
        ----------
        """
        conn, cursor = self.get_connect()
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        result = cursor.fetchone()
        self.close_connect(conn, cursor)
        return result

    def select_all(self, sql, args=None):
        """select_all方法用于查找所有记录

        Parameters
        ----------
        sql : str
            sql语句
        args : list or None
            参数
        Returns
        ----------
        """
        conn, cursor = self.get_connect()
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        result = cursor.fetchall()
        self.close_connect(conn, cursor)
        return result

    def excute(self, sql, value=None):
        """excute方法用于增删查改

        Parameters
        ----------
        sql : str
            sql 语句
        value : list or None
            值列表
        Returns
        ----------
        """
        conn, cursor = self.get_connect()
        try:
            res = cursor.execute(sql, value)
            conn.commit()
            self.close_connect(conn, cursor)
            return res
        except Exception as e:
            conn.rollock()
            raise e