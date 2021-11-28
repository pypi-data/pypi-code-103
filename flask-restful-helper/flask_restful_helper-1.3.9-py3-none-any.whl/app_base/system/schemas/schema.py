from flask_restful_helper import fields
from marshmallow import post_load, ValidationError

from apps.system.models import model
from main.extension import ma


class User(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = model.User
        exclude = ('password',)

    password1 = ma.Str(load_only=True, required=True)
    password2 = ma.Str(load_only=True, required=True)
    is_superuser = ma.Boolean(dump_only=True)
    theme = fields.JsonField()

    @post_load
    def ensure_password(self, data, **kwargs):
        if 'password1' in data and 'password2' in data:
            if data['password1'] != data['password2']:
                raise ValidationError('Passwords do not matched')
            else:
                data['password'] = data['password1']
                data.pop('password1')
                data.pop('password2')
        return data


class UserLogin(ma.Schema):
    username = ma.Str(required=True)
    password = ma.Str(required=True)


class Locale(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = model.Locale
