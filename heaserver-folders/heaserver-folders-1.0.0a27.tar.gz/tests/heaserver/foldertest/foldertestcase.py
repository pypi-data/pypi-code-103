from heaserver.service.testcase import mockmongotestcase, expectedvalues
from heaserver.service import wstl, appproperty
from heaserver.service.representor import cj
from heaserver.folder import service
from heaobject import user
from heaobject.root import HEAObject
from heaobject.folder import Folder
from yarl import URL
from aiohttp import hdrs, web
from typing import Dict, Any, List, Union, Type, Optional
import copy

db_values = {service.MONGODB_ITEMS_COLLECTION: [{
    'created': None,
    'derived_by': None,
    'derived_from': [],
    'description': None,
    'display_name': 'Reximus',
    'id': '666f6f2d6261722d71757578',
    'invites': [],
    'modified': None,
    'name': 'reximus',
    'owner': user.NONE_USER,
    'shares': [],
    'source': None,
    'type': 'heaobject.folder.Item',
    'version': None,
    'actual_object_type_name': 'heaobject.folder.Folder',
    'actual_object_id': '666f6f2d6261722d71757579',
    'folder_id': 'root'
},
    {
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'id': '0123456789ab0123456789ab',
        'invites': [],
        'modified': None,
        'name': 'reximus',
        'owner': user.NONE_USER,
        'shares': [],
        'source': None,
        'type': 'heaobject.folder.Item',
        'version': None,
        'actual_object_type_name': 'heaobject.folder.Folder',
        'actual_object_id': '0123456789ab0123456789ac',
        'folder_id': 'root'
    }
], service.MONGODB_FOLDER_COLLECTION: [{
    'created': None,
    'derived_by': None,
    'derived_from': [],
    'description': None,
    'display_name': 'Reximus',
    'id': '666f6f2d6261722d71757579',
    'invites': [],
    'modified': None,
    'name': 'reximus',
    'owner': user.NONE_USER,
    'shares': [],
    'source': None,
    'type': 'heaobject.folder.Folder',
    'version': None,
    'mime_type': 'application/x.folder'
},
    {
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'id': '0123456789ab0123456789ac',
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
]}

content_ = [{'collection': {'version': '1.0', 'href': 'http://localhost:8080/folders/root/items/', 'items': [{'data': [
    {'name': 'created', 'value': None, 'prompt': 'created', 'display': True},
    {'name': 'derived_by', 'value': None, 'prompt': 'derived_by', 'display': True},
    {'name': 'derived_from', 'value': [], 'prompt': 'derived_from', 'display': True},
    {'name': 'description', 'value': None, 'prompt': 'description', 'display': True},
    {'name': 'display_name', 'value': 'Reximus', 'prompt': 'display_name', 'display': True},
    {'name': 'id', 'value': '666f6f2d6261722d71757578', 'prompt': 'id', 'display': False},
    {'name': 'invites', 'value': [], 'prompt': 'invites', 'display': True},
    {'name': 'modified', 'value': None, 'prompt': 'modified', 'display': True},
    {'name': 'name', 'value': 'reximus', 'prompt': 'name', 'display': True},
    {'name': 'owner', 'value': 'system|none', 'prompt': 'owner', 'display': True},
    {'name': 'shares', 'value': [], 'prompt': 'shares', 'display': True},
    {'name': 'source', 'value': None, 'prompt': 'source', 'display': True},
    {'name': 'version', 'value': None, 'prompt': 'version', 'display': True},
    {'name': 'actual_object_type_name', 'value': 'heaobject.folder.Folder', 'prompt': 'actual_object_type_name',
     'display': True},
    {'name': 'actual_object_id', 'value': '666f6f2d6261722d71757579', 'prompt': 'actual_object_id', 'display': True},
    {'name': 'folder_id', 'value': 'root', 'prompt': 'folder_id', 'display': True},
    {'section': 'actual_object', 'name': 'created', 'value': None, 'prompt': 'created', 'display': True},
    {'section': 'actual_object', 'name': 'derived_by', 'value': None, 'prompt': 'derived_by', 'display': True},
    {'section': 'actual_object', 'name': 'derived_from', 'value': [], 'prompt': 'derived_from', 'display': True},
    {'section': 'actual_object', 'name': 'description', 'value': None, 'prompt': 'description', 'display': True},
    {'section': 'actual_object', 'name': 'display_name', 'value': 'Reximus', 'prompt': 'display_name', 'display': True},
    {'section': 'actual_object', 'name': 'id', 'value': '666f6f2d6261722d71757579', 'prompt': 'id', 'display': False},
    {'section': 'actual_object', 'name': 'invites', 'value': [], 'prompt': 'invites', 'display': True},
    {'section': 'actual_object', 'name': 'modified', 'value': None, 'prompt': 'modified', 'display': True},
    {'section': 'actual_object', 'name': 'name', 'value': 'reximus', 'prompt': 'name', 'display': True},
    {'section': 'actual_object', 'name': 'owner', 'value': 'system|none', 'prompt': 'owner', 'display': True},
    {'section': 'actual_object', 'name': 'shares', 'value': [], 'prompt': 'shares', 'display': True},
    {'section': 'actual_object', 'name': 'source', 'value': None, 'prompt': 'source', 'display': True},
    {'section': 'actual_object', 'name': 'version', 'value': None, 'prompt': 'version', 'display': True},
    {'section': 'actual_object', 'name': 'mime_type', 'value': 'application/x.folder', 'prompt': 'mime_type',
     'display': True}], 'links': [{'prompt': 'Move', 'rel': 'mover',
                                   'href': 'http://localhost:8080/folders/root/items/666f6f2d6261722d71757578/mover'},
                                  {'prompt': 'Open', 'rel': 'hea-opener-choices',
                                   'href': 'http://localhost:8080/folders/root/items/666f6f2d6261722d71757578/opener'},
                                  {'prompt': 'Duplicate', 'rel': 'duplicator',
                                   'href': 'http://localhost:8080/folders/root/items/666f6f2d6261722d71757578/duplicator'}]}],
                            'template': {'prompt': 'Properties', 'rel': 'properties', 'data': [
                                {'name': 'id', 'value': '666f6f2d6261722d71757578', 'prompt': 'Id', 'required': True,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'source', 'value': None, 'prompt': 'Source', 'required': False,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'version', 'value': None, 'prompt': 'Version', 'required': False,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'display_name', 'value': 'Reximus', 'prompt': 'Name', 'required': True,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'description', 'value': None, 'prompt': 'Description', 'required': False,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'owner', 'value': 'system|none', 'prompt': 'Owner', 'required': False,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'created', 'value': None, 'prompt': 'Created', 'required': False,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'modified', 'value': None, 'prompt': 'Modified', 'required': False,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'invites', 'value': [], 'prompt': 'Share invites', 'required': False,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'shares', 'value': [], 'prompt': 'Shared with', 'required': False,
                                 'readOnly': False, 'pattern': ''},
                                {'name': 'derived_by', 'value': None, 'prompt': 'Derived by', 'required': False,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'derived_from', 'value': [], 'prompt': 'Derived from', 'required': False,
                                 'readOnly': True, 'pattern': ''},
                                {'name': 'items', 'value': None, 'prompt': 'Items', 'required': False, 'readOnly': True,
                                 'pattern': ''}]}}}, {
                'collection': {'version': '1.0', 'href': 'http://localhost:8080/folders/root/items/', 'items': [{
                                                                                                                    'data': [
                                                                                                                        {
                                                                                                                            'name': 'created',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'created',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'derived_by',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'derived_by',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'derived_from',
                                                                                                                            'value': [],
                                                                                                                            'prompt': 'derived_from',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'description',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'description',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'display_name',
                                                                                                                            'value': 'Reximus',
                                                                                                                            'prompt': 'display_name',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'id',
                                                                                                                            'value': '0123456789ab0123456789ab',
                                                                                                                            'prompt': 'id',
                                                                                                                            'display': False},
                                                                                                                        {
                                                                                                                            'name': 'invites',
                                                                                                                            'value': [],
                                                                                                                            'prompt': 'invites',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'modified',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'modified',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'name',
                                                                                                                            'value': 'reximus',
                                                                                                                            'prompt': 'name',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'owner',
                                                                                                                            'value': 'system|none',
                                                                                                                            'prompt': 'owner',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'shares',
                                                                                                                            'value': [],
                                                                                                                            'prompt': 'shares',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'source',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'source',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'version',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'version',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'actual_object_type_name',
                                                                                                                            'value': 'heaobject.folder.Folder',
                                                                                                                            'prompt': 'actual_object_type_name',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'actual_object_id',
                                                                                                                            'value': '0123456789ab0123456789ac',
                                                                                                                            'prompt': 'actual_object_id',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'name': 'folder_id',
                                                                                                                            'value': 'root',
                                                                                                                            'prompt': 'folder_id',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'created',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'created',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'derived_by',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'derived_by',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'derived_from',
                                                                                                                            'value': [],
                                                                                                                            'prompt': 'derived_from',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'description',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'description',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'display_name',
                                                                                                                            'value': 'Reximus',
                                                                                                                            'prompt': 'display_name',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'id',
                                                                                                                            'value': '0123456789ab0123456789ac',
                                                                                                                            'prompt': 'id',
                                                                                                                            'display': False},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'invites',
                                                                                                                            'value': [],
                                                                                                                            'prompt': 'invites',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'modified',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'modified',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'name',
                                                                                                                            'value': 'reximus',
                                                                                                                            'prompt': 'name',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'owner',
                                                                                                                            'value': 'system|none',
                                                                                                                            'prompt': 'owner',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'shares',
                                                                                                                            'value': [],
                                                                                                                            'prompt': 'shares',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'source',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'source',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'version',
                                                                                                                            'value': None,
                                                                                                                            'prompt': 'version',
                                                                                                                            'display': True},
                                                                                                                        {
                                                                                                                            'section': 'actual_object',
                                                                                                                            'name': 'mime_type',
                                                                                                                            'value': 'application/x.folder',
                                                                                                                            'prompt': 'mime_type',
                                                                                                                            'display': True}],
                                                                                                                    'links': [
                                                                                                                        {
                                                                                                                            'prompt': 'Move',
                                                                                                                            'rel': 'mover',
                                                                                                                            'href': 'http://localhost:8080/folders/root/items/0123456789ab0123456789ab/mover'},
                                                                                                                        {
                                                                                                                            'prompt': 'Open',
                                                                                                                            'rel': 'hea-opener-choices',
                                                                                                                            'href': 'http://localhost:8080/folders/root/items/0123456789ab0123456789ab/opener'},
                                                                                                                        {
                                                                                                                            'prompt': 'Duplicate',
                                                                                                                            'rel': 'duplicator',
                                                                                                                            'href': 'http://localhost:8080/folders/root/items/0123456789ab0123456789ab/duplicator'}]}],
                               'template': {'prompt': 'Properties', 'rel': 'properties', 'data': [
                                   {'name': 'id', 'value': '0123456789ab0123456789ab', 'prompt': 'Id', 'required': True,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'source', 'value': None, 'prompt': 'Source', 'required': False,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'version', 'value': None, 'prompt': 'Version', 'required': False,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'display_name', 'value': 'Reximus', 'prompt': 'Name', 'required': True,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'description', 'value': None, 'prompt': 'Description', 'required': False,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'owner', 'value': 'system|none', 'prompt': 'Owner', 'required': False,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'created', 'value': None, 'prompt': 'Created', 'required': False,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'modified', 'value': None, 'prompt': 'Modified', 'required': False,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'invites', 'value': [], 'prompt': 'Share invites', 'required': False,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'shares', 'value': [], 'prompt': 'Shared with', 'required': False,
                                    'readOnly': False, 'pattern': ''},
                                   {'name': 'derived_by', 'value': None, 'prompt': 'Derived by', 'required': False,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'derived_from', 'value': [], 'prompt': 'Derived from', 'required': False,
                                    'readOnly': True, 'pattern': ''},
                                   {'name': 'items', 'value': None, 'prompt': 'Items', 'required': False,
                                    'readOnly': True, 'pattern': ''}]}}}]

content = {
    service.MONGODB_ITEMS_COLLECTION: {
        '666f6f2d6261722d71757578': content_
    },
    service.MONGODB_FOLDER_COLLECTION: {
        '666f6f2d6261722d71757579': content_
    }
}


def create_expected() -> Dict[str, Any]:
    result = copy.deepcopy(db_values)
    for item in result[service.MONGODB_ITEMS_COLLECTION]:
        item['actual_object'] = next(
            obj for obj in result[service.MONGODB_FOLDER_COLLECTION] if obj['id'] == item['actual_object_id'])
    return result


db_values_expected = create_expected()

ItemPostTestCase = \
    mockmongotestcase.get_test_case_cls(
        href='/folders/666f6f2d6261722d71757578/items?type=heaobject.folder.Folder',
        wstl_package=service.__package__,
        coll=service.MONGODB_ITEMS_COLLECTION,
        fixtures=db_values,
        body_post=expectedvalues.body_post(fixtures=db_values,
                                           coll=service.MONGODB_ITEMS_COLLECTION))

ItemGetTestCase = \
    mockmongotestcase.get_test_case_cls(href='http://localhost:8080/folders/root/items/',
                                        wstl_package=service.__package__,
                                        coll=service.MONGODB_ITEMS_COLLECTION,
                                        fixtures=db_values,
                                        content=content,
                                        content_type=cj.MIME_TYPE,
                                        expected_all=expectedvalues.expected_all(fixtures={
                                            service.MONGODB_ITEMS_COLLECTION: [
                                                db_values_expected[service.MONGODB_ITEMS_COLLECTION][0]]},
                                            coll=service.MONGODB_ITEMS_COLLECTION,
                                            wstl_builder=wstl.builder(
                                                package=service.__package__,
                                                href='http://localhost:8080/folders/root/items/'),
                                            get_all_actions=[
                                                expectedvalues.ActionSpec(
                                                    name='heaserver-folders-folder-get-properties',
                                                    rel=['properties']),
                                                expectedvalues.ActionSpec(
                                                    name='heaserver-folders-folder-get-open-choices',
                                                    url='http://localhost:8080/folders/root/items/{id}/opener',
                                                    rel=['hea-opener-choices']),
                                                expectedvalues.ActionSpec(
                                                    name='heaserver-folders-item-move',
                                                    url='http://localhost:8080/folders/root/items/{id}/mover',
                                                    rel=['mover']),
                                                expectedvalues.ActionSpec(
                                                    name='heaserver-folders-folder-duplicate',
                                                    url='http://localhost:8080/folders/root/items/{id}/duplicator',
                                                    rel=['duplicator'])],
                                            include_root=True) +
                                                     expectedvalues.expected_all(fixtures={
                                                         service.MONGODB_ITEMS_COLLECTION: [
                                                             db_values_expected[service.MONGODB_ITEMS_COLLECTION][1]]},
                                                         coll=service.MONGODB_ITEMS_COLLECTION,
                                                         wstl_builder=wstl.builder(
                                                             package=service.__package__,
                                                             href='http://localhost:8080/folders/root/items/'),
                                                         get_all_actions=[
                                                             expectedvalues.ActionSpec(
                                                                 name='heaserver-folders-folder-get-properties',
                                                                 rel=['properties']),
                                                             expectedvalues.ActionSpec(
                                                                 name='heaserver-folders-folder-get-open-choices',
                                                                 url='http://localhost:8080/folders/root/items/{id}/opener',
                                                                 rel=['hea-opener-choices']),
                                                             expectedvalues.ActionSpec(
                                                                 name='heaserver-folders-item-move',
                                                                 url='http://localhost:8080/folders/root/items/{id}/mover',
                                                                 rel=['mover']),
                                                             expectedvalues.ActionSpec(
                                                                 name='heaserver-folders-folder-duplicate',
                                                                 url='http://localhost:8080/folders/root/items/{id}/duplicator',
                                                                 rel=['duplicator'])],
                                                         include_root=True),
                                        expected_one=expectedvalues.expected_one(fixtures=db_values_expected,
                                                                                 coll=service.MONGODB_ITEMS_COLLECTION,
                                                                                 wstl_builder=wstl.builder(
                                                                                     package=service.__package__,
                                                                                     href='http://localhost:8080/folders/root/items'),
                                                                                 get_actions=[
                                                                                     expectedvalues.ActionSpec(
                                                                                         name='heaserver-folders-folder-get-properties',
                                                                                         rel=['properties']),
                                                                                     expectedvalues.ActionSpec(
                                                                                         name='heaserver-folders-folder-get-open-choices',
                                                                                         url='http://localhost:8080/folders/root/items/{id}/opener',
                                                                                         rel=['hea-opener-choices']),
                                                                                     expectedvalues.ActionSpec(
                                                                                         name='heaserver-folders-item-move',
                                                                                         url='http://localhost:8080/folders/root/items/{id}/mover',
                                                                                         rel=['mover']),
                                                                                     expectedvalues.ActionSpec(
                                                                                         name='heaserver-folders-folder-duplicate',
                                                                                         url='http://localhost:8080/folders/root/items/{id}/duplicator',
                                                                                         rel=['duplicator'])],
                                                                                 include_root=True),
                                        expected_one_duplicate_form=expectedvalues.expected_one_duplicate_form(
                                            fixtures=db_values_expected,
                                            coll=service.MONGODB_ITEMS_COLLECTION,
                                            duplicate_action_name='heaserver-folders-folder-duplicate-form',
                                            include_root=True,
                                            wstl_builder=wstl.builder(package=service.__package__,
                                                                      href='http://localhost:8080/folders/root/items/')),
                                        body_put=expectedvalues.body_put(fixtures=db_values_expected,
                                                                         coll=service.MONGODB_ITEMS_COLLECTION),
                                        put_content_status=404)


async def mock_type_to_resource_url(request: web.Request, type_or_type_name: Union[str, Type[HEAObject]]) -> Optional[
    str]:
    if type_or_type_name in ('heaobject.folder.Folder', Folder):
        return str(URL('http://' + request.headers[hdrs.HOST]).with_path('/folders'))
    else:
        return None


service.type_to_resource_url = mock_type_to_resource_url


async def mock_get_actual_item(request, wstl_builder, item, headers=None):
    actions = [
        {
            "name": "heaserver-folders-folder-get-open-choices",
            "description": "Open this folder",
            "type": "safe",
            "action": "read",
            "target": "item read cj",
            "prompt": "Open",
            "href": '/folders/{folder_id}/items/{id}/opener',
            "rel": "hea-opener-choices"
        },
        {
            "name": "heaserver-folders-folder-get-properties",
            "description": "View and edit this folder's properties",
            "type": "unsafe",
            "target": "item cj-template",
            "action": "update",
            "prompt": "Properties",
            "href": "#",
            "rel": "properties",
            "inputs": [
                {
                    "name": "id",
                    "prompt": "Id",
                    "required": True,
                    "readOnly": True
                },
                {
                    "name": "source",
                    "prompt": "Source"
                },
                {
                    "name": "version",
                    "prompt": "Version"
                },
                {
                    "name": "display_name",
                    "prompt": "Name",
                    "required": True
                },
                {
                    "name": "description",
                    "prompt": "Description",
                    "type": "textarea"
                },
                {
                    "name": "owner",
                    "prompt": "Owner"
                },
                {
                    "name": "created",
                    "prompt": "Created",
                    "readOnly": True
                },
                {
                    "name": "modified",
                    "prompt": "Modified",
                    "readOnly": True
                },
                {
                    "name": "invites",
                    "prompt": "Share invites",
                    "readOnly": True
                },
                {
                    "name": "shares",
                    "prompt": "Shared with"
                },
                {
                    "name": "derived_by",
                    "prompt": "Derived by",
                    "readOnly": True
                },
                {
                    "name": "derived_from",
                    "prompt": "Derived from",
                    "readOnly": True
                },
                {
                    "name": "items",
                    "prompt": "Items",
                    "readOnly": True
                }
            ]
        },
        {
            "name": "heaserver-folders-folder-duplicate",
            "description": "Duplicate this folder",
            "type": "unsafe",
            "action": "append",
            "target": "item read cj",
            "prompt": "Duplicate",
            "href": "/folders/{folder_id}/items/{id}/duplicator",
            "rel": "duplicator"
        }
    ]
    _mock_add_actions(actions, wstl_builder, request)
    return _get_data([item])


def _mock_add_actions(actions, wstl_builder, request):
    for action in actions:
        if not wstl_builder.has_design_time_action(action['name']):
            wstl_builder.add_design_time_action(action)
        if not wstl_builder.has_run_time_action(action['name']):
            wstl_builder.add_run_time_action(action['name'],
                                             path=action['href'],
                                             root=request.app[appproperty.HEA_COMPONENT],
                                             rel=action.get('rel', None))


async def mock_get_actual_item_duplicate(request, wstl_builder, item, headers=None):
    actions = [
        {
            "name": "heaserver-folders-folder-duplicate-form",
            "description": "Duplicate this folder",
            "type": "unsafe",
            "target": "item cj-template",
            "action": "update",
            "prompt": "Duplicate",
            "href": '/folders/root/items/'
        }
    ]
    _mock_add_actions(actions, wstl_builder, request)
    return _get_data([item])


service._add_actual_object = mock_get_actual_item
service._add_actual_object_duplicate_form = mock_get_actual_item_duplicate


def _get_data(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    For an item, attempts to find the item's corresponding folder, and returns the copy of the item with its
    actual_object attribute set to the folder in a list of length 1.
    :param item: an Item object.
    :return: a list containing a copy of the item with the corresponding actual folder, or an empty list if the folder
    could not be found.
    """
    result = []
    for item in items:
        for folder in db_values[service.MONGODB_FOLDER_COLLECTION]:
            if item['actual_object_id'] == folder['id']:
                item['actual_object'] = folder
                result.append(item)
    return result
