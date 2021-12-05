# pylint: skip-file
import asyncio
import unittest

from fastapi.testclient import TestClient

from unimatrix.ext import webapi
from .. import ResourceEndpointSet
from .. import __unimatrix__ as boot
from ..asgi import Application


class SubresourceTestCase(unittest.TestCase):

    class view_class(ResourceEndpointSet):
        require_authentication = False

        @webapi.action
        async def index_action(self):
            pass

        @webapi.action(detail=True)
        async def detail_action(self, **kwargs):
            pass

    def setUp(self):
        asyncio.run(boot.on_setup())
        self.app = Application(
            allowed_hosts=['*'],
            enable_debug_endpoints=True
        )
        self.client = TestClient(self.app)
        self.view_class.add_to_router(self.app, '/test')

    def test_action_url_exists(self):
        response = self.client.get('/test/index-action')
        self.assertEqual(response.status_code, 200)

    def test_detail_action_url_exists(self):
        response = self.client.get('/test/1/detail-action')
        self.assertEqual(response.status_code, 200)
