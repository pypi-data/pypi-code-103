from apps.system.logics import logic
from flask_jwt_extended import jwt_required

from flask_restful_helper import ApiView


class User(ApiView):
    _logic = logic.User
    method_decorators = {
        'GET': jwt_required,
        'PUT': jwt_required,
        'PATCH': jwt_required,
        'DELETE': jwt_required
    }

class Login(ApiView):
    _logic = logic.Login


class Locale(ApiView):
    _logic = logic.Locale
