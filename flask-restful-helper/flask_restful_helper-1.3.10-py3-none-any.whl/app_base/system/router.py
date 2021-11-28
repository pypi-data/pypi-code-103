from apps.system.api_views import api_view
from flask import Blueprint
from flask_restful_helper import Api

blueprint = Blueprint('system', __name__, url_prefix='/system')
api = Api(blueprint)
api.add_resource(api_view.User, '/users', endpoint='users', methods=['GET', 'POST'])
api.add_resource(api_view.User, '/users/<pk>', endpoint='users_pk', methods=['GET', 'PUT', 'PATCH', 'DELETE'])

api.add_resource(api_view.Login, '/login', endpoint='login', methods=['POST'])

api.add_resource(api_view.Locale, '/locales', endpoint='locales', methods=['GET', 'POST'])
api.add_resource(api_view.Locale, '/locales/<pk>', endpoint='locales_pk', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
