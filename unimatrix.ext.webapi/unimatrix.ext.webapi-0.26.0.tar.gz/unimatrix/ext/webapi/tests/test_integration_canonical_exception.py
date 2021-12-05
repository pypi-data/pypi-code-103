# pylint: skip-file
import unittest

from fastapi.testclient import TestClient
from ioc.exc import UnsatisfiedDependency
from unimatrix.ext.model.exc import CanonicalException

from ..asgi import Application


class CanonicalExceptionTestCase(unittest.TestCase):

    class exception_class(CanonicalException):
        http_status_code = 511
        code = 'TEST_EXCEPTION'

    def setUp(self):
        self.app = Application(
            allowed_hosts=['*']
        )
        self.client = TestClient(self.app)
        self.app.add_api_route(
            '/unsatisfied',
            self.raise_unsatisfied_dependency
        )
        self.app.add_api_route(
            '/exception',
            self.raise_canonical
        )

    async def raise_canonical(self):
        raise self.exception_class

    async def raise_unsatisfied_dependency(self):
        raise UnsatisfiedDependency

    def test_canonical_exception_returns_status_code(self):
        response = self.client.get('/exception')
        self.assertEqual(response.status_code, self.exception_class.http_status_code)

    def test_canonical_exception_returns_header(self):
        response = self.client.get('/exception')
        self.assertIn('X-Canonical-Exception', response.headers)

    def test_canonical_exception_returns_code(self):
        response = self.client.get('/exception')
        dto = response.json()
        self.assertEqual(dto['code'], self.exception_class.code)

    def test_unsatisfied_dependency_returns_status_code(self):
        response = self.client.get('/unsatisfied')
        self.assertEqual(response.status_code, 503)

    def test_unsatisfied_dependency_returns_code(self):
        response = self.client.get('/unsatisfied')
        dto = response.json()
        self.assertEqual(dto['code'], 'FEATURE_NOT_SUPPORTED')
