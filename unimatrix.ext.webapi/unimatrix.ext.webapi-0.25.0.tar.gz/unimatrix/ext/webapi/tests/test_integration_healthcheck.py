# pylint: skip-file
import unittest

from fastapi.testclient import TestClient

from ..asgi import Application


class CanonicalExceptionTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Application(
            allowed_hosts=['*']
        )
        self.client = TestClient(self.app)

    def test_liveness_returns_200(self):
        response = self.client.get('/.well-known/health/live')
        self.assertEqual(response.status_code, 200)

    def test_readyness_returns_200(self):
        response = self.client.get('/.well-known/health/ready')
        self.assertEqual(response.status_code, 200)
