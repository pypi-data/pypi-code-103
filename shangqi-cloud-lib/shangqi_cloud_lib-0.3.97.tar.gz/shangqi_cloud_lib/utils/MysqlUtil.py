import os

import pymysql
import logging
import traceback
import mysql.connector
from shangqi_cloud_lib.context import config
from shangqi_cloud_lib.utils.DBUtil import BaseSession, echo_sql
from shangqi_cloud_lib.utils.FileUtil import read_text


def mysql_connect(host, user, port, db, pwd, charset):
    try:
        if not db:
            db = config.mysql_database
        if not host:
            host = config.mysql_ip
        if not user:
            user = config.mysql_user
        if not port:
            port = config.mysql_port
        if not pwd:
            pwd = config.mysql_password
        if not charset:
            charset = "utf8"
        conn = pymysql.connect(
            host=host,
            user=user,
            port=port,
            database=db,
            password=pwd,
            # auth_plugin='mysql_native_password',
            charset=charset
        )
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        logging.warning("连接数据库异常:" + traceback.format_exc())
        return "", str(e)


def create_table(sql_file):
    table = sql_file.split(os.path.sep)[-1].replace(".sql", "")
    sql = "select count(*) from information_schema.tables where table_schema='{}' and table_name = '{}'".format(
        config.mysql_database, table)
    with SqlSession() as session:
        exist = session.query_one(sql, "first")
        if exist == 0:
            create_sql = read_text(sql_file)
            session.execute_update(create_sql.strip())


class SqlSession(BaseSession):
    def __init__(self, host=None, user=None, port=None, db=None, pwd=None, charset=None, auto_commit=True):
        super().__init__("mysql", auto_commit)
        self.conn, self.cursor = mysql_connect(host, user, port, db, pwd, charset)
        if self.conn == "":
            raise Exception(self.cursor)


# 根据sql更新数据，包括插入、修改、删除
def query_update(sql, id=False, host=None, user=None, port=None, db=None, pwd=None, charset=None):
    try:
        conn, cursor = mysql_connect(host, user, port, db, pwd, charset)
        if conn != "":
            cursor.execute(sql)
            res = 1
            if id:
                cursor.execute("SELECT @@IDENTITY as id")
                res = cursor.fetchone()[0]
            conn.commit()
            mysql_close(conn, cursor)
            return res
    except:
        logging.warning("[" + sql + "] sql异常!")
        logging.warning(traceback.format_exc())
    return None


def mysql_close(conn, cursor):
    cursor.close()
    conn.close()
