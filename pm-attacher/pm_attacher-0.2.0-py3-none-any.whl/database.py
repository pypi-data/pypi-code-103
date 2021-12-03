import pymssql


class Database(object):
    def __init__(self, server, port, name, username, password):
        self.connection = pymssql.connect(host=server, port=port, user=username, password=password, database=name)

    def execute_query(self, sql: str, params: tuple = ..., as_dict=False):
        cursor = self.connection.cursor(as_dict=as_dict)
        if params is ...:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)

        return cursor

    def select_all(self, sql: str, params: tuple = ..., as_dict=False):
        cursor = self.execute_query(sql, params, as_dict)
        return cursor.fetchall()

    def select_one(self, sql: str, params: tuple = ..., as_dict=False):
        cursor = self.execute_query(sql, params, as_dict)
        return cursor.fetchone()
