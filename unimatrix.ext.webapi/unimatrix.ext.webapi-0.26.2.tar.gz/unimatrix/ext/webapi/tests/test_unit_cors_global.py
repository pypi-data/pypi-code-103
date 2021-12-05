# pylint: skip-file
import unittest

from fastapi.testclient import TestClient

from ..asgi import Application


class GlobalCorsTestCase(unittest.TestCase):
    origin = "http://example.com"

    def setUp(self):
        self.app = Application(
            allowed_hosts=['*']
        )
        self.app.add_api_route('/', self.request_handler)
        self.client = TestClient(self.app)

    async def request_handler(self):
        pass

    def test_allows_origin(self):
        self.app.enable_cors(
            allow_origins=[self.origin]
        )
        response = self.client.get(
            '/',
            headers={
                'Host': "example.com",
                'Origin': "http://example.com",
            }
        )
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'], self.origin)
