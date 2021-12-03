# -*- coding: utf-8 -*-
from collective.embeddedpage.interfaces import ICollectiveEmbeddedpageLayer
from collective.embeddedpage.interfaces import IEmbeddedPage
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(IEmbeddedPage, ICollectiveEmbeddedpageLayer)
class CustomSerializeToJson(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        serialization = super(CustomSerializeToJson, self).__call__(
            version=version, include_items=include_items
        )
        view = getMultiAdapter((self.context, self.request), name="view")
        data = view.process_page()
        serialization.update(
            {
                "text": {
                    "data": safe_unicode(data["content"]),
                    "content-type": data["content-type"],
                    "encoding": "utf-8",
                },
            }
        )
        return serialization
