# pylint: skip-file
import unittest

from fastapi.testclient import TestClient
from ioc.exc import UnsatisfiedDependency

from ..asgi import Application


class ConnectionRefusedErrorTestCase(unittest.TestCase):
    exception_class = ConnectionRefusedError
    http_status_code = 503
    code = 'SERVICE_NOT_AVAILABLE'

    def setUp(self):
        self.app = Application(
            allowed_hosts=['*']
        )
        self.client = TestClient(self.app)
        self.app.add_api_route(
            '/exception',
            self.raise_exception
        )

    async def raise_exception(self):
        raise self.exception_class

    def test_exception_returns_error_code(self):
        response = self.client.get('/exception')
        dto = response.json()
        self.assertEqual(dto['code'], self.code)

    def test_exception_returns_status_code(self):
        response = self.client.get('/exception')
        self.assertEqual(
            response.status_code,
            self.http_status_code
        )


class ConnectionResetErrorTestCase(ConnectionRefusedErrorTestCase):
    exception_class = ConnectionResetError


class BrokenPipeErrorTestCase(ConnectionRefusedErrorTestCase):
    exception_class = BrokenPipeError


class ConnectionAbortedErrorTestCase(ConnectionRefusedErrorTestCase):
    exception_class = ConnectionAbortedError
