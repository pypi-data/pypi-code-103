from flask import Blueprint
from flask_restful_helper import Api

blueprint = Blueprint('file', __name__, url_prefix='/file')
api = Api(blueprint)

