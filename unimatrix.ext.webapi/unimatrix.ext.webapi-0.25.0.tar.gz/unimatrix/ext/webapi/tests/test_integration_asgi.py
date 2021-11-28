# pylint: skip-file
import unittest

from fastapi.testclient import TestClient

from ..asgi import Application


class ApplicationConfigurationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Application(
            allowed_hosts=['*']
        )
        self.client = TestClient(self.app)

    def test_docs_url_defaults(self):
        response = self.client.get('/ui')
        self.assertEqual(response.status_code, 200)

    def test_openapi_url_defaults(self):
        response = self.client.get('/openapi.json')
        self.assertEqual(response.status_code, 200)
