# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


import sqlite3

from threading import Lock

from rains.common.db.const import ConstDatabaseTaskNaming
from rains.common.db.const import ConstDatabaseCaseNaming
from rains.common.db.const import ConstDatabaseTableNaming

from rains.common.const import ConstPath
from rains.common.decorator import singleton_pattern


@singleton_pattern
class Database(object):
    """
    [ 数据库 ]
    * 基于 SQLite 数据库。

    """

    _conn: sqlite3.Connection = None
    """ SQLite数据库连接对象 """

    _lock: Lock = Lock()
    """ 数据库互斥锁 """

    def __init__(self):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        try:
            # 创建当前项目的日志根目录
            if not ConstPath.DATA.is_dir():
                ConstPath.DATA.mkdir(parents=True, exist_ok=True)

            # 单例创建/连接数据库
            if not self._conn:
                self.connect()
                self._conn.commit()

        except BaseException as e:
            raise Exception(f'SQLite数据库初始化异常:: { e } ')

    def read(self, sql: str) -> list:
        """
        [ 读取 ]
        * 执行只读查询语句，该函数不会获取数据库互斥锁。

        [ 必要参数 ]
        * sql (str) : SQLite 查询语句

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 查询结果列表

        """

        try:
            # 创建数据库游标
            cur = self._conn.cursor()
            # 执行查询语句
            cur.execute(sql)
            # 获取查询结果
            data = cur.fetchall()
            # 注销数据库游标
            cur.close()

            return data

        except BaseException as e:
            raise Exception(f'SQLite数据库读取异常:: { e } ')

    def write(self, sql: str) -> int:
        """
        [ 写入 ]
        * 执行互斥写入语句，该函数执行时会获取数据库互斥锁，结束时释放。

        [ 必要参数 ]
        * sql (str) : SQLite 语句

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 写入数据后返回该条数据的自增ID

        """

        try:
            # 获取锁
            with self._lock:

                # 创建数据库游标
                cur = self._conn.cursor()
                # 执行查询语句
                cur.execute(sql)
                # 获取数据自增ID
                aid = cur.lastrowid
                # 注销数据库游标
                cur.close()

                return aid

        except BaseException as e:
            raise Exception(f'SQLite数据库写入异常:: { e } ')

    def connect(self):
        """
        [ 数据库连接 ]
        * 无

        """

        # 创建数据库连接对象
        self._conn = sqlite3.connect(ConstPath.DB, check_same_thread=False)
        # 创建数据库游标
        Cur = self._conn.cursor()
        # 构建任务表
        Cur.execute(CreateTableSql.TASKS)
        # 构建用例表
        Cur.execute(CreateTableSql.CASES)
        # 注销数据库游标
        Cur.close()

    def commit(self):
        """
        [ 事务保存 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._conn.commit()

    def rollback(self):
        """
        [ 事务回滚 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._conn.rollback()

    def close(self):
        """
        [ 关闭数据库连接 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._conn.close()


class CreateTableSql(object):
    """
    [ 建表语句 ]
    * 无

    """

    TASKS = f"""
        
    CREATE TABLE IF NOT EXISTS { ConstDatabaseTableNaming.TASKS }
    (
        id                                        INTEGER PRIMARY KEY,
        { ConstDatabaseTaskNaming.NAME }          TEXT NOT NULL,
        { ConstDatabaseTaskNaming.REMARK }        TEXT NOT NULL,
        { ConstDatabaseTaskNaming.EXECUTE_DATE }  DATE NOT NULL,
        { ConstDatabaseTaskNaming.IS_COMPLETED }  BLOB NOT NULL,
        { ConstDatabaseTaskNaming.START_TIME }    DATE,
        { ConstDatabaseTaskNaming.END_TIME }      DATE,
        { ConstDatabaseTaskNaming.SPEND_TIME_S }  INTEGER,
        { ConstDatabaseTaskNaming.CASE_ALL }      INTEGER,
        { ConstDatabaseTaskNaming.CASE_PASS }     INTEGER,
        { ConstDatabaseTaskNaming.CASE_FAIL }     INTEGER
    );

    """

    """
    [ 创建任务表 ]
    * 记录任务的执行信息。

    [ 表结构 ]
    * id (int): 记录编号，随数据量而自增，无需手动输入
    * name (str): 任务名称，不可为空
    * remark (str): 任务备注信息，不可为空
    * execute_date (date): 执行日期，不可为空
    * is_completed (bool): 是否已完成，不可为空
    * start_time (date): 开始时间
    * end_time (date): 结束时间
    * spend_time_s (date): 消耗时间(秒)
    * case_all (int): 所有用例计数
    * case_pass (int): 成功的用例计数
    * case_fail (int): 失败用例数计数

    """

    CASES = f"""

    CREATE TABLE IF NOT EXISTS { ConstDatabaseTableNaming.CASES }
    (
        id                                        INTEGER PRIMARY KEY,
        { ConstDatabaseCaseNaming.TID }           INT NOT NULL,
        { ConstDatabaseCaseNaming.NAME }          TEXT NOT NULL,
        { ConstDatabaseCaseNaming.REMARK }        TEXT NOT NULL,
        { ConstDatabaseCaseNaming.STATE }         TEXT NOT NULL,
        { ConstDatabaseCaseNaming.EXECUTE_DATE }  DATE NOT NULL,
        { ConstDatabaseCaseNaming.START_TIME }    DATE,
        { ConstDatabaseCaseNaming.END_TIME }      DATE,
        { ConstDatabaseCaseNaming.SPEND_TIME_S }  INTEGER,
        { ConstDatabaseCaseNaming.RUN_STEP }      TEXT
    );
        
    """

    """
    [ 创建用例表 ]
    * 记录用例的执行信息。
    
    [ 表结构 ]
    * id (int): 记录编号，随数据量而自增，无需手动输入
    * tid (int): 所属的任务记录编号，不可为空
    * name (str): 用例名称，不可为空
    * remark (str): 用例备注信息，不可为空
    * state (str): 用例状态，不可为空
    * start_time (date): 开始时间
    * end_time (date): 结束时间
    * spend_time_s (date): 消耗时间(秒)
    * run_step (str): 运行步骤
            
    """
