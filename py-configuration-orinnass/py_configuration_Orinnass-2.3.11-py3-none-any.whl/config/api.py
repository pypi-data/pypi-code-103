from flask import Blueprint

api = Blueprint(__name__, __name__)
__base_api_url = '/api/config/'


@api.route(f'{__base_api_url}get')
def get_config():
    pass


@api.route(f'{__base_api_url}update_config')
def update_config():
    pass