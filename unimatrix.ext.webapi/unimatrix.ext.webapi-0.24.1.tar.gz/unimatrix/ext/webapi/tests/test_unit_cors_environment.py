# pylint: skip-file
import os
import unittest

from fastapi.testclient import TestClient

from ..asgi import Application


class EnvironmentCorsTestCase(unittest.TestCase):

    def setUp(self):
        self.environ = os.environ

    def get_asgi_client(self):
        app = Application(
            allowed_hosts=['*']
        )
        client = TestClient(app)
        app.add_api_route('/', self.request_handler, methods=['POST'])
        return client

    async def request_handler(self):
        pass

    def tearDown(self):
        os.environ = self.environ
