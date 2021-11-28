from flask import abort as _abort
from flask import jsonify
from flask import make_response
from flask_restful.utils import http_status_message


def abort(status_code, messages=None):
    if messages is None:
        messages = {'message': http_status_message(status_code)}
    response = make_response(jsonify(messages), status_code)
    _abort(status_code, response)
