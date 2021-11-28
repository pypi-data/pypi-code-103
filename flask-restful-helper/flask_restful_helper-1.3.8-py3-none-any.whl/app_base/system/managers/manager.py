from apps.system.models import model

from flask_restful_helper import Manager


class User(Manager):
    _model = model.User


class Api(Manager):
    _model = model.Api


class ApiRolePrivilege(Manager):
    _model = model.ApiRolePrivilege


class Locale(Manager):
    _model = model.Locale
