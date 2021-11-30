from bson import ObjectId
from cerberus import Validator
import datetime
from dgapi import DGAPI
from flask import jsonify, make_response, request, session
from functools import wraps
import jwt
from logging import error
from mongoCon import MongoCon
from utils.helpers import CustomErrorHandler, remove_dots


def is_authorize():
    return DGAPI.get('valid_token').status_code == 200


def login_required(f):
    """Full login"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('security-token')
        try:
            data = jwt.decode(token, '@3!f3719em$893&')  # token decode
        except Exception:   # jwt.ExpiredSignatureError
            error('TOKEN NO VALID')
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
        else:  # token valido
            session['user_id'] = data['user_id']
            session['user_application_id'] = data['user_application_id']
            session['user_name'] = data['name']
            session['user_email'] = data.get('email', '')
            session['roles'] = data.get('security_actions', [])
            if is_authorize():
                return f(*args, **kwargs)
            else:
                return make_response(jsonify({'error': 'Unauthorized access'}), 401)
    return decorated


def login_script(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('token', '')
        session['token'] = token
        if token == '5gABTw3tXCS{]NN[fk,dUWKcmr3,DaHoa[hiSTfVzq.cZp;W72B[CU.7,kqA(}':
            return f(*args, **kwargs)
        else:
            return make_response(jsonify({'error': 'Unauthorized access'}), 401)
    return decorated


def activity_log_decorator(msg=None):
    """
    Decorador para guardar en el log una entrada a un endpoint
    msg: Es un mensaje opcional
    """
    def inner_function(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data_log = {
                'user': session.get('user_name', 'Anonymous'),
                'endpoint': request.path,
                'values': remove_dots(request.json),
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
            return f(*args, **kwargs)
        return wrapper
    return inner_function


def validate_request(schema=None, origin='json', headers=False):
    """
    Decorador para validar un el request
    - schema: diccionario con el schema que debe cumplir la petición
    Por default los campos son requeridos
    """
    def inner_function(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            response = {}
            if headers:
                if isinstance(headers, bool):
                    local_headers = ["current-group", "current-dealer"]
                else:
                    local_headers = headers
                headers_missing = [header for header in local_headers if header not in request.headers]
                if len(headers_missing) > 0:
                    response['headers'] = {}
                    for param in headers_missing:
                        response['headers'][param] = 'Required header not found'
            if schema:
                schema_r = schema
                if origin == 'form':
                    validate_data = request.form.copy() if request.form else {}
                else:
                    validate_data = request.json.copy() if request.json else {}
                if isinstance(schema_r, dict):
                    if 'type' in schema and 'schema' in schema:
                        schema_r = {'data': schema}
                        validate_data = {'data': validate_data}
                    for value in schema_r.values():
                        if isinstance(value, dict):
                            if 'required' not in value:
                                value.update({'required': True})
                            if 'type' in value:
                                if value['type'] == 'custom_date':
                                    del value['type']
                                    format_ = value.pop('format', '%Y-%m-%d')
                                    value.update({
                                        'type': 'date',
                                        'coerce': lambda s: datetime.datetime.strptime(s, format_)
                                    })
                                elif value['type'] == 'object_id':
                                    del value['type']
                                    value.update({
                                        'type': 'string',
                                        'coerce': lambda s: str(ObjectId(s) if s else '')
                                    })
                else:
                    raise TypeError('The schema should be a dict')
                v = Validator(schema_r, error_handler=CustomErrorHandler)
                v.allow_unknown = True
                if not v.validate(validate_data) or response:
                    response = make_response(jsonify({**response, **v.errors}), 422)
            if response == {}:
                response = f(*args, **kwargs)
            return response
        return wrapper
    return inner_function


def validate_args(params):
    """
    Decorador para validar los parametros de un endpoint
    - params: array de strings con los parametros que debe contener la peticion
    """
    def inner_function(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            v = Validator()
            response = {}
            if v.validate({'data': params}, {'data': {'type': 'list', 'schema': {'type': 'string'}}}):
                params_missing = [param for param in params if param not in request.args]
                if len(params_missing) > 0:
                    response['params'] = {}
                    for param in params_missing:
                        response['params'][param] = 'Required field not found'
                    response = make_response(jsonify(response), 422)
                else:
                    response = f(*args, **kwargs)
            else:
                raise TypeError('The params should be a list of strings')
            return response
        return wrapper
    return inner_function
