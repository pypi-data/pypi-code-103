from flask import Blueprint, request, Response
from json import dumps, loads
from datetime import datetime
from database_connector import ConnectionsPool
from config import Configuration

api = Blueprint(__name__.replace('.', '-'), __name__)
__base_api = '/api/db_connection/'
__db_pool = ConnectionsPool()
__logger = Configuration().logging.get_logger(__name__)


def __connection_api_handler__(method):
    global __db_pool
    request_data = loads(request.data)

    connection = __db_pool.get_connection()
    try:
        response_sql_query = connection.__getattribute__(method)(**request_data)
        response = {
            "time_response": datetime.now().timestamp(),
            "code": 200,
            "result": response_sql_query
        }
        return Response(dumps(response), status=200, mimetype='application/json')
    except Exception as e:
        __logger.error(str(e), exc_info=True, stack_info=True)
    finally:
        connection.release()


@api.route(f"{__base_api}custom_sql", methods=["POST"])
def custom_sql():
    """
    Роут для выполнения кастомного sql запроса
    """
    return __connection_api_handler__('custom_sql')


@api.route(f"{__base_api}select", methods=["POST"])
def select():
    """
    Роут для выполнения select запроса
    """
    return __connection_api_handler__('select')


@api.route(f"{__base_api}insert", methods=["POST"])
def insert():
    """
    Роут для выполнения insert запроса
    """
    return __connection_api_handler__('insert')
