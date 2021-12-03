import os
from functools import wraps

import jwt
from flask import request
from flask_jwt_extended import verify_jwt_in_request, \
    verify_jwt_refresh_token_in_request, get_jwt_identity
from flask_jwt_extended.config import config as jwt_config
from flask_jwt_extended.exceptions import NoAuthorizationError, WrongTokenError
from http_status_code.standard import expired_token, \
    unauthorized_request, wrong_token, forbidden_request
from sqlalchemy import create_engine

from sqlalchemy.sql import text


class APIAuth:
    _engine = None
    table_name = 'session_token'

    @classmethod
    def _get_engine(cls):
        if cls._engine is None:
            cls._engine = create_engine(os.environ['JWT_SESSION_TOKEN_DB_URI'])
        return cls._engine

    @classmethod
    def _get_token(cls):
        auth_header = request.headers.get(jwt_config.header_name, None)
        if auth_header is None:
            raise NoAuthorizationError("Missing {} Header".format(jwt_config.header_name))
        return auth_header

    @classmethod
    def _validate_token(cls, token_type):
        if os.environ.get('JWT_SESSION_TOKEN_DB_URI') is not None:
            with cls._get_engine().connect() as con:
                statement = text(f"SELECT is_invalid FROM {cls.table_name} WHERE {token_type}_token=:token")
                row = con.execute(statement, token=cls._get_token()).fetchone()
                if row is None:
                    raise jwt.InvalidTokenError

                is_invalid = row[0]
                if is_invalid:
                    raise jwt.InvalidTokenError

    # A decorator for authentication and authorization purpose
    @classmethod
    def auth_required(cls, req_token='access', authentication_required=True, authorization_object=None):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                try:
                    if not authentication_required:
                        return fn(*args, **kwargs)

                    cls._validate_token(req_token)
                    if req_token == 'access':
                        verify_jwt_in_request()

                    elif req_token == 'refresh':
                        verify_jwt_refresh_token_in_request()

                    request.claims = get_jwt_identity()

                    if authorization_object is not None and not authorization_object.is_authorized():
                        return forbidden_request, None

                    return fn(*args, **kwargs)

                except (jwt.DecodeError, jwt.InvalidTokenError):
                    # Token is not a valid JWT token
                    return unauthorized_request, None

                except NoAuthorizationError:
                    # The token is not provided
                    return unauthorized_request, None

                except jwt.ExpiredSignatureError:
                    # The token is expired
                    return expired_token, None

                except WrongTokenError as e:
                    # To discriminate between refresh and access tokens
                    wrong_token.update_msg(str(e))
                    return wrong_token, None

            return wrapper

        return decorator
