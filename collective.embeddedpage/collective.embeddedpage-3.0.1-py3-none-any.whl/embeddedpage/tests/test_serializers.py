# -*- coding: utf-8 -*-
from collective.embeddedpage.testing import (
    COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING,
)  # noqa
from httmock import all_requests
from httmock import HTTMock
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter

import unittest


class TestCustomSerializeToJson(unittest.TestCase):

    layer = COLLECTIVE_EMBEDDEDPAGE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        with api.env.adopt_roles(["Manager"]):
            self.epage = api.content.create(
                container=self.portal,
                type="EmbeddedPage",
                id="epage",
                url="https://plone.org",
            )

    def serialize(self, obj):
        serializer = getMultiAdapter((obj, self.request), ISerializeToJson)
        return serializer()

    def test_serializer(self):
        @all_requests
        def response_link(url, request):
            return {
                "status_code": 200,
                "content": u"<div>Main Page</div>",
            }

        with HTTMock(response_link):
            data = self.serialize(self.epage)
        self.assertEqual(
            {
                "data": u"<div>Main Page</div>",
                "content-type": "text/html",
                "encoding": "utf-8",
            },
            data["text"],
        )
