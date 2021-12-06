import os
from typing import Optional
from urllib.parse import urljoin
import requests
from flask import Blueprint, request, Flask
from injector import Injector

import pytest
from unittest.mock import MagicMock

from ..authentication.middleware import ServiceMiddleware


def mock_middleware_server(views: Blueprint):

    def create_app():
        os.environ["CATALOGUE_API_URL"] = "test"
        application = Flask(__name__)
        application.wsgi_app = ServiceMiddleware(application.wsgi_app)
        application.injector = Injector()

        # we need to access the injector in the wsgi (early), so we ascribe it to the object too
        application.register_blueprint(views)
        application.wsgi_app.injector = application.injector

        return application

    return create_app()


@pytest.fixture
def disconnected_client():

    views = Blueprint('middleware', __name__)
    HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

    @views.route(
        '/',
        methods=HTTP_METHODS
    )
    @views.route(
        '/<path:optional_path>',
        methods=HTTP_METHODS
    )
    def test_route(optional_path: Optional[str] = None):
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {}
        resp.content = "HELLO, WORLD"
        return resp.content, resp.status_code, resp.headers.items()

    @views.route(
        '/direct_test',
        methods=HTTP_METHODS
    )
    def test_direct_route(optional_path: Optional[str] = None):
        resp = MagicMock()
        resp.status_code = 403
        resp.headers = {}
        resp.content = "BE GONE, DRAGON"
        return resp.content, resp.status_code, resp.headers.items()

    app = mock_middleware_server(views)
    with app.test_client() as client:
        yield client