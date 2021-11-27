# pylint: skip-file
import unittest

from fastapi.testclient import TestClient
from ..asgi import Application


class MetadataTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Application(allowed_hosts=['*'])
        self.client = TestClient(self.app)

        # ensure that there is an endpoint with path parameters.
        @self.app.get('/test/{foo}')
        async def f(foo: int):
            pass

    def test_self_endpoint_does_not_produce_errors(self):
        response = self.client.get('/.well-known/self')
        self.assertEqual(response.status_code, 200)
