# pylint: skip-file
import asyncio
import unittest

from fastapi.testclient import TestClient

from .. import ResourceEndpointSet
from .. import __unimatrix__ as boot
from ..asgi import Application


class SubresourceTestCase(unittest.TestCase):

    class view_class(ResourceEndpointSet):
        require_authentication = False

        class subresource_class(ResourceEndpointSet):
            require_authentication = False
            resource_name = 'subresource'
            path_parameter = 'subresource_id'

            async def index(self, resource_id: int):
                return {'resource_id': resource_id}

            async def retrieve(self, resource_id: int, subresource_id: int):
                return {'resource_id': resource_id, 'subresource_id': subresource_id}

        async def create(self):
            pass

        async def index(self):
            pass

        async def retrieve(self, resource_id):
            pass

        subresources = [subresource_class]

    def setUp(self):
        asyncio.run(boot.on_setup())
        self.app = Application(
            allowed_hosts=['*'],
            enable_debug_endpoints=True
        )
        self.client = TestClient(self.app)
        self.view_class.add_to_router(self.app, '/test')

    def test_subresource_index(self):
        response = self.client.get('/test/1/subresource')
        dto = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('resource_id', dto)
        self.assertEqual(dto['resource_id'], 1)

    def test_subresource_retrieve(self):
        response = self.client.get('/test/1/subresource/2')
        dto = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('resource_id', dto)
        self.assertIn('subresource_id', dto)
        self.assertEqual(dto['resource_id'], 1)
        self.assertEqual(dto['subresource_id'], 2)
