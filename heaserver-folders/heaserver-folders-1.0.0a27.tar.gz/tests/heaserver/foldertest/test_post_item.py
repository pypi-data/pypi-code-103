from aiohttp.test_utils import unittest_run_loop
from .foldertestcase import ItemPostTestCase
from heaobject import user
from heaserver.service.oidcclaimhdrs import SUB


class TestPostItem(ItemPostTestCase):

    async def setUpAsync(self):
        await super().setUpAsync()
        self.__body = {
            'created': None,
            'derived_by_uri': None,
            'derived_from_uris': [],
            'description': None,
            'display_name': 'Reximus',
            'invites': [],
            'modified': None,
            'name': 'reximus',
            'owner': user.NONE_USER,
            'shares': [],
            'source_uri': None,
            'type': 'heaobject.folder.Folder',
            'version': None
        }

    @unittest_run_loop
    async def test_post(self):
        obj = await self.client.request('POST',
                                        '/folders/root/items?type=heaobject.folder.Folder',
                                        json=self.__body,
                                        headers={SUB: user.NONE_USER})
        self.assertEqual('201: Created', await obj.text())

    @unittest_run_loop
    async def test_post_status(self):
        obj = await self.client.request('POST',
                                        '/folders/root/items?type=heaobject.folder.Folder',
                                        json=self.__body,
                                        headers={SUB: user.NONE_USER})
        self.assertEqual(201, obj.status)

    @unittest_run_loop
    async def test_post_status_empty_body(self):
        obj = await self.client.request('POST',
                                        '/folders/root/items?type=heaobject.folder.Folder',
                                        headers={SUB: user.NONE_USER})
        self.assertEqual(400, obj.status)

