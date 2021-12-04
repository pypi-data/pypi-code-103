#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_zfiles.synchronizer module

This module defines a synchronizer class, which is used to copy documents from
local container to a remote one.
"""

from xmlrpc.client import Binary, Fault

from persistent import Persistent
from zope.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty

from pyams_utils.adapter import adapter_config, get_annotation_adapter
from pyams_utils.factory import factory_config
from pyams_utils.protocol.xmlrpc import get_client
from pyams_zfiles.interfaces import DELETE_MODE, DOCUMENT_SYNCHRONIZER_KEY, IDocumentContainer, \
    IDocumentSynchronizer, IMPORT_MODE


__docformat__ = 'restructuredtext'


IMPORT_FIELDS = ('title', 'application_name', 'filename', 'properties',
                 'tags', 'status', 'owner', 'creator', 'created_time',
                 'access_mode', 'readers', 'update_mode', 'managers')


@factory_config(IDocumentSynchronizer)
class DocumentSynchronizer(Persistent, Contained):
    """Document synchronizer class"""

    target = FieldProperty(IDocumentSynchronizer['target'])
    username = FieldProperty(IDocumentSynchronizer['username'])
    _password = FieldProperty(IDocumentSynchronizer['password'])

    @property
    def password(self):
        """Password getter"""
        return self._password

    @password.setter
    def password(self, value):
        """Password setter"""
        if value == '****':
            return
        self._password = value

    def synchronize(self, oid, mode=IMPORT_MODE, request=None):  # pylint: disable=unused-argument
        """Synchronize given OID to remote container"""
        client = get_client(self.target, (self.username, self.password),
                            allow_none=True)
        try:
            if mode == IMPORT_MODE:
                document = self.__parent__.get_document(oid)
                data = Binary(document.data.data)
                properties = document.to_json(IMPORT_FIELDS)
                client.importFile(oid, data, properties)
            elif mode == DELETE_MODE:
                client.deleteFile(oid)
            return mode, 'OK'
        except Fault:
            return mode, 'ERROR'


@adapter_config(required=IDocumentContainer,
                provides=IDocumentSynchronizer)
def document_container_synchronizer(context):
    """Document container synchronizer adapter"""
    return get_annotation_adapter(context, DOCUMENT_SYNCHRONIZER_KEY, IDocumentSynchronizer)
