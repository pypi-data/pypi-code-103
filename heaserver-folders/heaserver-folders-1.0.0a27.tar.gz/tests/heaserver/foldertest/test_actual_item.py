from aiohttp.test_utils import unittest_run_loop
from aiohttp import web
from heaserver.service import runner, client
from heaserver.service.testcase.aiohttptestcase import HEAAioHTTPTestCase
from heaobject.folder import Folder
from heaobject import user
import json


class TestActualChild(HEAAioHTTPTestCase):

    async def setUpAsync(self):
        await super().setUpAsync()
        self.__body = {
            'created': None,
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'Reximus',
            'id': None,
            'invites': [],
            'modified': None,
            'name': 'reximus',
            'owner': user.NONE_USER,
            'shares': [],
            'source': None,
            'type': 'heaobject.folder.Folder',
            'version': None,
            'mime_type': 'application/x.folder'
        }

    async def get_application(self):
        async def test_folder_get(request):
            return web.Response(status=200,
                                body=json.dumps([self.__body]),
                                content_type='application/json')

        async def test_get(request):
            obj = await client.get(request.app, 'http://127.0.0.1:' + str(request.url.port) + '/folders', Folder)
            return web.Response(status=200,
                                body=obj.json_dumps() if obj is not None else None,
                                content_type='application/json')

        app = runner.get_application()
        app.router.add_get('/folders', test_folder_get)
        app.router.add_get('/testget', test_get)

        return app

    @unittest_run_loop
    async def test_get(self):
        obj = await self.client.request('GET', '/testget')
        self.assertEqual(self.__body, await obj.json())

