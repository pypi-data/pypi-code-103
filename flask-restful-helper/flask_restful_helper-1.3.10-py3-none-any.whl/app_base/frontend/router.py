from flask import Blueprint
from flask_restful_helper import Api

from apps.frontend.api_views import api_view

blueprint = Blueprint('frontend', __name__, url_prefix='/frontend')
api = Api(blueprint)
api.add_resource(api_view.Menu, '/menus', endpoint='menus', methods=['GET'])
