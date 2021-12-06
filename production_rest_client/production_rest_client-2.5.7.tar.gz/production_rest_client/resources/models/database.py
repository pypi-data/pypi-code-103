# coding=utf-8
# pylint: disable=broad-except, import-error
import pymysql as mysql
from DBUtils.PooledDB import PooledDB


class SqlConnection(object):

    pool = dict()

    def __init__(self, host="172.29.129.8", port=3306, user="tester", passwd="Cnex!321", db_name="production_test"):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db_name = db_name
        self.conn = self.__get_conn()
        self.cursor = self.conn.cursor()

    def __get_conn(self):
        if self.db_name not in SqlConnection.pool.keys():
            SqlConnection.pool[self.db_name] =  PooledDB(creator=mysql, mincached=1 , maxcached=20 ,
                                                         host=self.host , port=self.port, user=self.user,
                                                         passwd=self.passwd, db=self.db_name,
                                                         use_unicode=True,charset="utf8")
        return SqlConnection.pool[self.db_name].connection()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def execute_sql_command(self, command):
        results = list()
        try:
            self.conn.ping()
            self.cursor.execute(command)
            results = self.cursor.fetchall()
        except BaseException as message:
            print(message)
        return results

    def execute_and_commit_sql_command(self, command):
        results = list()
        try:
            self.conn.ping()
            self.cursor.execute(command)
            self.conn.commit()
            results = self.cursor.fetchall()
        except BaseException as message:
            print(message)
        return results

    def insert_to_table(self, table, fields):
        col_str = ""
        value_str = ""
        for key, value in fields.items():
            if value is False:
                value = "0"
            if value is True:
                value = "1"
            col_str = "`{}`".format(key) if col_str == "" else "{},`{}`".format(col_str, key)
            value_str = "'{}'".format(value) if value_str == "" else "{},'{}'".format(value_str, value)
        insert_command = "INSERT INTO {} ({}) VALUES({})".format(table, col_str, value_str)
        self.cursor.execute(insert_command)
        self.conn.commit()


if __name__ == '__main__':
    import json
    db = SqlConnection(db_name="web_testing")
    with open(r"E:\web\parameters.json", 'r') as load_f:
        load_dict = json.load(load_f)
        for item in load_dict:
            db.insert_to_table("test_platform_parameterconfig", item["fields"])
        pass

    pass