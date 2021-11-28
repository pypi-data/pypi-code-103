import json
from mysql.connector import Error, PoolError
from mysql.connector.pooling import PooledMySQLConnection
from .connector import MySQLConnector


class Query:
    SELECT_ONE = 'SELECT_ONE'
    SELECT_MANY = 'SELECT_MANY'
    UPDATE = 'UPDATE'
    CREATE = 'CREATE'
    DELETE = 'DELETE'

    def __init__(self, sql: str, args: dict or tuple or None, type: str = SELECT_ONE):
        self.sql = sql
        self.args = args
        self.type = type

    def __str__(self):
        return json.dumps({'query': self.sql, 'args': self.args, 'type': self.type})


class QueryResponse:
    SUCCESS = 0
    FAIL = 1

    def __init__(self, response: list | dict | None, response_message: str = None, response_code: int = None,
                 conn: PooledMySQLConnection = None):
        self.result: list | dict | None = response
        self.message: str = response_message
        self.code: int = response_code
        self.conn: PooledMySQLConnection = conn


def execute(queries: list[Query], conn: PooledMySQLConnection = None, do_commit: bool = True) -> QueryResponse:
    if not queries:
        return QueryResponse(response=None,
                             response_message='no query provided!',
                             response_code=QueryResponse.FAIL)

    results = []
    response_code = QueryResponse.SUCCESS
    response_message = None

    try:
        if conn is None:
            conn = MySQLConnector.get_connection()
    except PoolError as e:
        response_message, response_code = e.msg, e.errno
        return QueryResponse(response=None, response_message=response_message, response_code=response_code)

    try:
        for q in queries:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(q.sql, q.args)
            if q.type == Query.SELECT_ONE:
                data = cursor.fetchone()
            elif q.type == Query.SELECT_MANY:
                data = cursor.fetchall()
            elif q.type == Query.UPDATE or q.type == Query.DELETE:
                data = {'row_count': cursor.rowcount}
            else:  # CREATE
                data = {'last_row_id': cursor.lastrowid}
            results.append(data)
            cursor.close()

        if do_commit: conn.commit()

    except Error as e:
        conn.rollback()
        results = None
        response_message, response_code = e.msg, e.errno
    finally:
        query_response = QueryResponse(
            response=None if results is None else results[0] if len(queries) == 1 else results,
            response_message=response_message,
            response_code=response_code)

        if do_commit or response_code != QueryResponse.SUCCESS:
            conn.close()
        else:
            query_response.conn = conn

        return query_response
