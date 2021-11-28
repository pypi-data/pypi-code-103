from datetime import timedelta

from apps.system.managers import manager
from apps.system.schemas import schema
from flask_jwt_extended import create_access_token
from main.extension import bcrypt, db_helper

from flask_restful_helper import Logic


class User(Logic):
    _manager = manager.User
    _schema = schema.User

    def create(self, data, query_args, *args, **kwargs):
        with db_helper.auto_commit():
            data = self.validate(data)
            data['password'] = bcrypt.generate_password_hash(data['password'])
            data = self.manager.create(data)
        return {'data': self.schema.dump(data)}, 201


class Login(Logic):
    _manager = manager.User
    _schema = schema.UserLogin

    def create(self, data, query_args, *args, **kwargs):
        data = self.validate(data)
        user = self.manager.retrieve(username=data.get('username'))
        if user and bcrypt.check_password_hash(user.password, data.get('password')):
            user_claims = {'user': schema.User().dump(user)}
            obj = {
                'access_token': create_access_token(identity=user.id, expires_delta=timedelta(minutes=100),
                                                    additional_claims=user_claims)
            }
            return {'data': obj}, 200
        else:
            return {'message': 'Username and password do not match or you do not have an account yet'}, 401


class Locale(Logic):
    _manager = manager.Locale
    _schema = schema.Locale
