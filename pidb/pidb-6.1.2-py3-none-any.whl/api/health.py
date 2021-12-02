import pkg_resources

from flask import url_for
from flask import current_app
from flask import Blueprint
from flask_restx import Api
from flask_restx import Resource
from flask_restx import fields
from sqlalchemy.exc import SQLAlchemyError

from . import RegisteredApi

blueprint = Blueprint('health_api', __name__)


api = Api(
    blueprint,
    version='1.0',
    title='Population Imaging Database health REST API',
    description='The Population Imaging Database is for storing result of population imaging studies.',
    default_mediatype='application/json'
)


@api.route('/healthy', endpoint='healthy')
class Healthy(Resource):
    @api.doc('Endpoint to check if flask app is running')
    @api.response(200, 'Healthy')
    def get(self):
        return


@api.route('/ready', endpoint='ready')
class Ready(Resource):
    @api.doc('Endpoint to check if flask app ready (e.g. all resources are available and functioning)')
    @api.response(200, 'Ready')
    @api.response(500, 'Not ready')
    def get(self):
        try:
            from pidb import models
            models.Finding.query.one_or_none()
            return None
        except SQLAlchemyError:
            return None, 500


versions_model = {
    'version': fields.String,
    'api_versions': fields.Raw,
}


@api.route('/versions', endpoint='versions')
class Versions(Resource):
    @api.doc('Versions of the APIs available')
    @api.response(200, 'Success')
    @api.marshal_with(versions_model)
    def get(self):
        versions = {k: url_for(f"{v.name}.root") for k, v in RegisteredApi.api_map.items()}
        return {
            'version': pkg_resources.require('pidb')[0].version,
            'api_versions': versions

        }
