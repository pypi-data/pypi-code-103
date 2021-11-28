import traceback

from flask import jsonify
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import Api as _Api
from flask_restful.utils import http_status_message
from flask_restful_helper.restful_helper.response import make_response
from jwt.exceptions import ExpiredSignatureError, DecodeError
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, MethodNotAllowed, HTTPException, NotFound


class Api(_Api):
    def handle_error(self, e):
        """It helps preventing writing unnecessary
        try/except block though out the application
        """
        # Handle HTTPExceptions
        if isinstance(e, ValidationError):
            messages = e.normalized_messages()
            for key in messages.keys():
                messages[key] = messages[key][0]
            return make_response(jsonify({'message': messages}), 400)
        elif isinstance(e, NotFound):
            return make_response(jsonify({'message': 'The requested resource does not exist'}, e.code))
        elif isinstance(e, BadRequest):
            if hasattr(e,'data'):
                return make_response(jsonify({'message': e.data.get('message')}), e.code)
            if hasattr(e, 'description'):
                return make_response(jsonify({'message': e.description}), e.code)
            return make_response(jsonify({'message': e.data.get('message')}), e.code)
        elif isinstance(e, MethodNotAllowed):
            return make_response(jsonify({'message': http_status_message(e.code)}), e.code)
        elif isinstance(e, AppException):
            return make_response(jsonify({'message': e.description}), e.status_code)
        elif isinstance(e, HTTPException):
            if hasattr(e, 'description') and e.description is not None:
                return getattr(e, 'description')
        elif isinstance(e, IntegrityError):
            return make_response(jsonify({'message': http_status_message(409)}), 409)
        elif isinstance(e, ExpiredSignatureError) or isinstance(e, NoAuthorizationError):
            return make_response(jsonify({'message': str(e)}), 401)
        elif isinstance(e, DecodeError):
            return make_response(jsonify({'message': str(e)}), 422)
        else:
            traceback.print_exc()
            # print(e.__dict__)
            return make_response(jsonify({'message': str(e)}), 500)


class AppException(Exception):
    status_code = 500

    def __init__(self, description=None, status_code=None):
        super(BaseException, self).__init__()
        if status_code is not None:
            self.status_code = status_code
        self.description = description

    def to_dict(self):
        return dict(self.description or ())
