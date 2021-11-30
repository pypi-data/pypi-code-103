from flask import request, session
from bson import ObjectId
from cerberus import errors
from datetime import date, datetime, timedelta
import decimal
import json
from os import path
from random import choice
from string import digits, ascii_letters
from traceback import StackSummary, walk_tb
from const import ROOT_API
from mongoCon import MongoCon


class CustomJSONEncoder(json.JSONEncoder):

    DATE_FORMAT = r'%Y-%m-%d'
    DATETIME_FORMAT = r'%Y-%m-%d %H:%M:%S'

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return round(float(obj), 2)
        elif isinstance(obj, datetime):
            return obj.strftime(self.DATETIME_FORMAT)
        elif isinstance(obj, date):
            return obj.strftime(self.DATE_FORMAT)
        elif isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


class CustomErrorHandler(errors.BasicErrorHandler):
    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.REQUIRED_FIELD.code] = 'required field not found'


def create_string(ln=15, allow_special=False):
    """Create random string"""
    special_char = "!#$%&*+-=?@^_|"
    if allow_special:
        string = ''.join(choice(ascii_letters + digits + special_char) for _ in range(ln))
    else:
        string = ''.join(choice(ascii_letters + digits) for _ in range(ln))
    return string


def last_day_of_month(month, year):
    """
    Esta funcion retorna el ultimo día del mes dado
    - month: numero de mes
    - year: numero del
    """
    new_month = month + 1 if month < 12 else 1
    new_year = year if month < 12 else year + 1
    return datetime(new_year, new_month, 1) - timedelta(seconds=1)


def date_range_query(start_date, end_date, date_format: str = '%Y-%m-%d'):
    """
    This function return a dictionary with the format to search in the range of start_date and end_date
    - start_date(string): Fecha inicial del rango a buscar
    - end_date(string): Fecha final del rango a buscar
    - format(string): Formato en el que se encuentran las fechas
    """
    return {
        '$gte': datetime.strptime(start_date, date_format),
        '$lt': datetime.strptime(end_date, date_format) + timedelta(days=1) - timedelta(milliseconds=1)
    }


def month_range_query(month, year):
    """
    Esta funcion retorna un diccionario con el formato para hacer una busqueda por todas las fechas del mes dado
    - month: mes del año
    - year: year a buscar
    """
    return {
        '$gte': datetime(year, month, 1),
        '$lt': last_day_of_month(month, year)
    }


def find_in_arr_by_dict(arr, search_dict, key_name='_id'):
    """
    Esta funcion busca un elemento en el array apartir de un diccionario de busqueda, sino lo encuentra retorna None
    - arr: array de diccionarios
    - search_dict: diccionario de datos a buscar
    - key_name(opcional): Llave sobre la que se hara la busqueda. La llave sobre la que se busca tambien debe ser un diccionario
    """
    result = None
    for element in arr:
        add = True
        for key in search_dict:
            if key not in element[key_name] or element[key_name][key] != search_dict[key]:
                add = False
        if add:
            result = element
            break
    return result


def docs_path(controller, filename):
    """
    Esta funcion regresa el directorio donde se guardaran las plantillas para la documentación
    de un controlador
    - controller: nombre del controlador
    - filename: nombre del archivo
    """
    return path.join(ROOT_API, "modules", controller, "docs", filename)


def valid_filename_or_next(directory, file_name):
    """
    Esta funcion valida que el file_name no exista en el directorio, si existe, busca el siguiente nombre disponible
    - directory: Directorio donde se validara el archivo
    - file_name: Nombre del archivo a validar
    """
    new_file_name = file_name
    if path.exists(path.join(directory, file_name)):
        version = 1
        valid = False
        file, ext = file_name.rsplit('.', 1)
        while not valid:
            new_file_name = "{} ({}).{}".format(file, version, ext)
            if path.exists(path.join(directory, new_file_name)):
                version += 1
            else:
                valid = True
    return new_file_name


def remove_dots(data):
    """
    Esta funcion remueve los puntos
    - data: diccionario
    """
    if isinstance(data, dict):
        return {remove_dots(key): value if isinstance(value, str) else remove_dots(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [remove_dots(element) for element in data]
    elif isinstance(data, str):
        return data.replace('.', '||')
    else:
        return data


def error_manager(error):
    """
    Esta funcion retorna un diccionario con los datos del error
    - error
    """
    stack_trace = []
    for trace in StackSummary.extract(walk_tb(error.__traceback__), capture_locals=True):
        stack_trace.append({
            'File': trace.filename,
            'Line': trace.lineno,
            'Function': trace.name,
            'Message': trace.line,
            'Locals': trace.locals
        })
    user = session.get('user_name', request.headers.get('user-logged-in', 'Anonymous'))
    return {
        'endpoint': request.path,
        'values': remove_dots(request.json),
        'Error type': type(error).__name__,
        'Error message': str(error),
        'Stack trace': stack_trace,
        'user': user,
        'date': datetime.now(),
    }


def activity_log_function(collection, action, data, msg=None):
    """
    Funcion para guardar en el log una acción que modifique la base de datos
    collection: Colleción que sera modificada
    action: Acción realizada sobre la colección
    data: Datos utilizados
    msg: Es un mensaje opcional
    """
    user = request.headers.get('user-logged-in', 'Anonymous')
    data_log = {
        'user': user,
        'endpoint': request.path,
        'collection': collection,
        'action': action,
        'data': remove_dots(data),
        'date': datetime.datetime.now(),
        'server_protocol': request.environ.get('SERVER_PROTOCOL', None),
        'request_method': request.environ.get('REQUEST_METHOD', None),
        'remote_addr': request.environ.get('REMOTE_ADDR', None),
        'remote_port': request.environ.get('REMOTE_PORT', None),
        'content_type': request.environ.get('CONTENT_TYPE', None),
        'http_user_agent': request.environ.get('HTTP_USER_AGENT', '')
    }
    if msg is not None:
        data_log['message'] = msg
    with MongoCon() as cnx:
        cnx.activity_log.insert_one(data_log)
