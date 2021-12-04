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

"""PyAMS_zfiles.api.rest module

This module defines ZFiles REST API.
"""

import base64
import sys

from colander import DateTime, Int, MappingSchema, OneOf, SchemaNode, String, drop
from cornice import Service
from cornice.validators import colander_body_validator, colander_querystring_validator
from pyramid.httpexceptions import HTTPBadRequest, HTTPCreated, HTTPForbidden, HTTPNotFound, \
    HTTPOk

from pyams_utils.registry import get_utility
from pyams_utils.rest import DateRangeSchema, FileUploadType, PropertiesMapping, StringListSchema
from pyams_zfiles.interfaces import ACCESS_MODE_IDS, ARCHIVED_STATE, CREATE_DOCUMENT_PERMISSION, \
    CREATE_DOCUMENT_WITH_OWNER_PERMISSION, DELETED_STATE, DRAFT_STATE, IDocumentContainer, \
    PUBLISHED_STATE, READ_DOCUMENT_PERMISSION, REST_CONTAINER_ROUTE, REST_DOCUMENT_ROUTE


__docformat__ = 'restructuredtext'

from pyams_zfiles import _


TEST_MODE = sys.argv[-1].endswith('/test')


class ErrorSchema(MappingSchema):
    """Base error schema"""


class FieldsNamesSchema(MappingSchema):
    """Properties names schema"""
    fields = StringListSchema(title=_("List of requested fields names"),
                              missing=drop)


class BaseDocumentSchema(MappingSchema):
    """Base document schema"""
    title = SchemaNode(String(),
                       title=_("Document title"),
                       missing=drop)
    application_name = SchemaNode(String(),
                                  title=_("Source application name"),
                                  missing=drop)
    filename = SchemaNode(String(),
                          title=_("File name"),
                          missing=drop)
    properties = SchemaNode(PropertiesMapping(),
                            title=_("Document custom properties"),
                            missing=drop)
    tags = StringListSchema(title=_("List of document tags"),
                            missing=drop)
    owner = SchemaNode(String(),
                       title=_("Current document owner"),
                       missing=drop)
    status = SchemaNode(String(),
                        title=_("Document status"),
                        validator=OneOf((DRAFT_STATE, PUBLISHED_STATE, ARCHIVED_STATE,
                                         DELETED_STATE)),
                        default=DRAFT_STATE,
                        missing=drop)
    access_mode = SchemaNode(String(),
                             title=_("Access mode"),
                             validator=OneOf(ACCESS_MODE_IDS),
                             default='private',
                             missing=drop)
    readers = StringListSchema(title=_("Document readers IDs"),
                               missing=drop)
    update_mode = SchemaNode(String(),
                             title=_("Update mode"),
                             validator=OneOf(ACCESS_MODE_IDS),
                             default='private',
                             missing=drop)
    managers = StringListSchema(title=_("Document managers IDs"),
                                missing=drop)


class DocumentDataSchema(BaseDocumentSchema):
    """Document data update schema"""
    data = SchemaNode(FileUploadType(),
                      title=_("Document data; may be provided in Base64 when using JSON"),
                      missing=drop)
    filename = SchemaNode(String(),
                          title=_("File name"),
                          missing=drop)


class NewDocumentSchema(DocumentDataSchema):
    """New document schema"""
    title = SchemaNode(String(),
                       title=_("Document title"))
    application_name = SchemaNode(String(),
                                  title=_("Source application name"))
    filename = SchemaNode(String(),
                          title=_("Document file name"))
    data = SchemaNode(FileUploadType(),
                      title=_("Document data; may be provided in Base64 when using JSON"))


class ImportDocumentSchema(NewDocumentSchema):
    """Import document schema"""
    created_time = SchemaNode(DateTime(),
                              title=_("Document creation timestamp"))
    owner = SchemaNode(String(),
                       title=_("Current document owner"))


class DocumentSchema(BaseDocumentSchema):
    """Document schema"""
    api = SchemaNode(String(), title=_("Document base REST API URL"))
    oid = SchemaNode(String(), title=_("Document unique identifier"))
    version = SchemaNode(Int(), title=_("Document version"))
    href = SchemaNode(String(), title=_("Absolute URL of document data file"))
    hash = SchemaNode(String(), title=_("SHA512 hash of document data file"))
    filesize = SchemaNode(Int(), title=_("Document file size"))
    content_type = SchemaNode(String(), title=_("Document content type"))
    creator = SchemaNode(String(), title=_("Document creator principal ID"))
    created_time = SchemaNode(DateTime(), title=_("Document creation timestamp"))
    owner = SchemaNode(String(), title=_("Current document owner"))
    updater = SchemaNode(String(), title=_("Last document updater principal ID"))
    updated_time = SchemaNode(DateTime(), title=_("Last document update timestamp"))
    status_updater = SchemaNode(String(), title=_("Last workflow status updater principal ID"))
    status_update_time = SchemaNode(DateTime(), title=_("Last document status update timestamp"))


class DocumentSearchSchema(MappingSchema):
    """Document search schema"""
    oid = StringListSchema(title=_("Document unique identifiers"),
                           missing=drop)
    version = SchemaNode(Int(),
                         title=_("Document version"),
                         missing=drop)
    title = SchemaNode(String(),
                       title=_("Document title"),
                       missing=drop)
    application_name = SchemaNode(String(),
                                  title=_("Source application name"),
                                  missing=drop)
    hash = SchemaNode(String(),
                      title=_("SHA512 hash of document data file"),
                      missing=drop)
    properties = SchemaNode(PropertiesMapping(),
                            title=_("Document properties, provided as a mapping"),
                            missing=drop)
    tags = StringListSchema(title=_("Document tags, separated with semicolons"),
                            missing=drop)
    status = SchemaNode(String(),
                        title=_("Document status"),
                        validator=OneOf((DRAFT_STATE, PUBLISHED_STATE, ARCHIVED_STATE,
                                         DELETED_STATE)),
                        default=DRAFT_STATE,
                        missing=drop)
    creator = SchemaNode(String(),
                         title=_("Document creator principal ID"),
                         missing=drop)
    created_date = DateRangeSchema(title=_("Document creation dates range"),
                                   missing=drop)
    owner = SchemaNode(String(),
                       title=_("Current document owner"),
                       missing=drop)
    updater = SchemaNode(String(),
                         title=_("Last document updater principal ID"),
                         missing=drop)
    updated_date = DateRangeSchema(title=_("Document last update dates range"),
                                   missing=drop)
    status_updater = SchemaNode(String(),
                                title=_("Last workflow status updater principal ID"),
                                missing=drop)
    status_update_date = DateRangeSchema(title=_("Last workflow status update dates range"),
                                         missing=drop)
    fields = StringListSchema(title=_("List of requested field names"),
                              missing=drop)


document_responses = {
    HTTPOk.code: DocumentSchema(description=_("Document properties")),
    HTTPCreated.code: DocumentSchema(description=_("Document created")),
    HTTPNotFound.code: ErrorSchema(description=_("Document not found")),
    HTTPForbidden.code: ErrorSchema(description=_("Forbidden access")),
    HTTPBadRequest.code: ErrorSchema(description=_("Missing arguments")),
}

if TEST_MODE:
    service_params = {}
else:
    service_params = {
        'response_schemas': document_responses
    }


container_service = Service(name=REST_CONTAINER_ROUTE,
                            pyramid_route=REST_CONTAINER_ROUTE,
                            description="ZFiles container service")


@container_service.get(require_csrf=False,
                       content_type=('application/json', 'multipart/form-data'),
                       validators=(colander_body_validator,),
                       schema=DocumentSearchSchema(),
                       **service_params)
def find_documents(request):
    """Find documents matching specified properties"""
    properties = request.params.copy() if TEST_MODE else request.validated.copy()
    fields = properties.pop('fields', None)
    container = get_utility(IDocumentContainer)
    return list(map(lambda x: x.to_json(fields),
                    container.find_documents(properties)))


@container_service.post(require_csrf=False,
                        content_type=('application/json', 'multipart/form-data'),
                        schema=NewDocumentSchema(),
                        validators=(colander_body_validator,),
                        **service_params)
def create_document(request):
    """Create new ZFiles document using multipart/form-data encoding"""
    container = get_utility(IDocumentContainer)
    if not request.has_permission(CREATE_DOCUMENT_PERMISSION, context=container):
        raise HTTPForbidden()
    properties = request.params.copy() if TEST_MODE else request.validated.copy()
    if request.headers.get('Content-Type').startswith('multipart/form-data'):
        properties['data'] = request.params.get('data')
    else:
        properties['data'] = base64.b64decode(request.json.get('data'))
    data = properties.pop('data', None)
    document = container.add_document(data, properties, request)
    result = document.to_json()
    request.response.status = HTTPCreated.code
    request.response.headers['location'] = result['api']
    return result


document_service = Service(name=REST_DOCUMENT_ROUTE,
                           pyramid_route=REST_DOCUMENT_ROUTE,
                           description="ZFiles document service")


def get_ids(request):
    """Get document ID and version from request path"""
    oid = request.matchdict['oid']
    if not oid:
        raise HTTPBadRequest()
    version = request.matchdict['version']
    if version:
        version = version[0]
    return oid, version or None


@document_service.get(require_csrf=False,
                      schema=FieldsNamesSchema(),
                      validators=(colander_body_validator, colander_querystring_validator),
                      **service_params)
def get_document(request):
    """Retrieve existing document information"""
    container = get_utility(IDocumentContainer)
    document = container.get_document(*get_ids(request))
    if document is None:
        raise HTTPNotFound()
    if not request.has_permission(READ_DOCUMENT_PERMISSION, context=document):
        raise HTTPForbidden()
    fields = request.params.get('fields') if TEST_MODE else request.validated.get('fields')
    if isinstance(fields, str):
        fields = set(fields.split(';'))
    return document.to_json(fields)


@document_service.post(require_csrf=False,
                       content_type=('application/json', 'multipart/form-data'),
                       schema=ImportDocumentSchema(),
                       validators=(colander_body_validator,),
                       **service_params)
def import_document(request):
    """Import document from other ZFiles database"""
    container = get_utility(IDocumentContainer)
    if not request.has_permission(CREATE_DOCUMENT_WITH_OWNER_PERMISSION, context=container):
        raise HTTPForbidden()
    properties = request.params.copy() if TEST_MODE else request.validated.copy()
    if request.headers.get('Content-Type').startswith('multipart/form-data'):
        properties['data'] = request.params.get('data')
    else:
        properties['data'] = base64.b64decode(request.json.get('data'))
    oid = request.matchdict['oid']
    data = properties.pop('data', None)
    document = container.import_document(oid, data, properties, request)
    result = document.to_json()
    request.response.status = HTTPCreated.code
    request.response.headers['location'] = result['api']
    return result


@document_service.patch(require_csrf=False,
                        content_type=('application/json', 'multipart/form-data'),
                        schema=BaseDocumentSchema(),
                        validators=(colander_body_validator,),
                        **service_params)
def patch_document(request):
    """Update existing document properties, excluding file data"""
    oid, version = get_ids(request)
    container = get_utility(IDocumentContainer)
    properties = request.params.copy() if TEST_MODE else request.validated.copy()
    document = container.update_document(oid, version, properties=properties, request=request)
    if document is None:
        return {
            'oid': oid,
            'status': 'deleted'
        }
    return document.to_json()


@document_service.put(require_csrf=False,
                      content_type=('application/json', 'multipart/form-data'),
                      schema=DocumentDataSchema(),
                      validators=(colander_body_validator,),
                      **service_params)
def put_document(request):
    """Update existing document content"""
    oid, version = get_ids(request)
    container = get_utility(IDocumentContainer)
    properties = request.params.copy() if TEST_MODE else request.validated.copy()
    if request.headers.get('Content-Type').startswith('multipart/form-data'):
        properties['data'] = request.params.get('data')
    else:
        properties['data'] = base64.b64decode(request.json.get('data'))
    data = properties.pop('data')
    document = container.update_document(oid, version, data, properties, request)
    if document is None:
        return {
            'oid': oid,
            'status': 'deleted'
        }
    return document.to_json()


@document_service.delete(require_csrf=False,
                         **service_params)
def delete_document(request):
    """Delete existing document content"""
    oid, _version = get_ids(request)
    container = get_utility(IDocumentContainer)
    container.delete_document(oid)
    return {
        'oid': oid,
        'status': 'deleted'
    }
