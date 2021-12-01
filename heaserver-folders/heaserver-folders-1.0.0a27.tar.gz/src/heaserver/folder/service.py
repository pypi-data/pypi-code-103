from heaserver.service.runner import init_cmd_line, routes, start
from heaserver.service.db import mongo, mongoservicelib
from heaserver.service.wstl import builder_factory, action, RuntimeWeSTLDocumentBuilder
from heaserver.service import client, response, appproperty, requestproperty, wstl
from heaserver.service.heaobjectsupport import new_heaobject, type_to_resource_url
from heaserver.service.oidcclaimhdrs import SUB
from heaserver.service.representor import wstljson
from heaserver.service.appproperty import HEA_DB
from heaobject.folder import Folder, Item
from heaobject.error import DeserializeException
from heaobject.root import Permission, type_for_name
from aiohttp import hdrs, web
from aiohttp.client_exceptions import ClientResponseError
from yarl import URL
from typing import Dict, Any, Optional
import logging
import copy

_logger = logging.getLogger(__name__)

MONGODB_FOLDER_COLLECTION = 'folders'
MONGODB_ITEMS_COLLECTION = 'folders_items'
SETTER_PERMS = [Permission.COOWNER.name, Permission.EDITOR.name]

ROOT_FOLDER = Folder()
ROOT_FOLDER.id = 'root'


async def _get_folder(request: web.Request) -> web.Response:
    """
    Gets the folder with the specified id.
    :param request: the HTTP request.
    :return: the requested folder or Not Found.
    """
    _logger.debug('Requested folder %s', request.match_info["id"])
    if request.match_info['id'] == 'root':
        return ROOT_FOLDER
    else:
        return await mongoservicelib.get(request, MONGODB_FOLDER_COLLECTION)


@routes.get('/folders/{id}')
@action(name='heaserver-folders-folder-get-open-choices', path='/folders/{folder_id}/items/{id}/opener', rel='hea-opener-choices')
@action(name='heaserver-folders-folder-get-properties', rel='properties')
@action(name='heaserver-folders-folder-duplicate', rel='duplicator', path='/folders/{folder_id}/items/{id}/duplicator')
async def get_folder(request: web.Request) -> web.Response:
    """
    Gets the folder with the specified id.
    :param request: the HTTP request.
    :return: the requested folder or Not Found.
    ---
    summary: A specific folder.
    tags:
        - heaserver-folders-get-folder
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_folder(request)


@routes.get('/folders/byname/{name}')
async def get_folder_by_name(request: web.Request) -> web.Response:
    """
    Gets the folder with the specified name.
    :param request: the HTTP request.
    :return: the requested folder or Not Found.
    ---
    summary: A specific folder.
    tags:
        - heaserver-folders-get-folder-by-name
    parameters:
        - $ref: '#/components/parameters/name'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get_by_name(request, MONGODB_FOLDER_COLLECTION)


@routes.get('/folders/{folder_id}/items')
@routes.get('/folders/{folder_id}/items/')
@action(name='heaserver-folders-item-move', path='/folders/{folder_id}/items/{id}/mover', include_root=True, rel='mover')
async def get_items(request: web.Request) -> web.Response:
    """
    Gets the items of the folder with the specified id.
    :param request: the HTTP request.
    :return: the requested items, or Not Found if the folder was not found.
    ---
    summary: All items in a folder.
    tags:
        - heaserver-folders-get-all-folder-items
    parameters:
        - name: folder_id
          in: path
          required: true
          description: The id of the folder to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A folder id
              value: root
    responses:
      '200':
        $ref: '#/components/responses/200'
    """
    folder = request.match_info['folder_id']
    _logger.debug('Requested items from the "%s" folder', folder)
    items = await request.app[appproperty.HEA_DB].get_all(request,
                                                          MONGODB_ITEMS_COLLECTION,
                                                          var_parts='folder_id',
                                                          sub=request.headers.get(SUB))
    _logger.debug('got items from mongo: %s', items)
    result = []
    wstl_builder = request[requestproperty.HEA_WSTL_BUILDER]
    for item in items:
        wstl_builder_ = copy.deepcopy(wstl_builder)
        wstl_builder_.data = [item]
        if await _add_actual_object(request, wstl_builder_, item, headers={SUB: request.headers.get(SUB)}):
            result.append(wstl_builder_())
    _logger.debug('got from service: %s', result)
    return await response.get_all_from_wstl(request, result)


@routes.get('/folders/{folder_id}/items/{id}')
@action(name='heaserver-folders-item-move', path='/folders/{folder_id}/items/{id}/mover', include_root=True, rel='mover')
async def get_item(request: web.Request) -> web.Response:
    """
    Gets the requested item from the given folder.

    :param request: the HTTP request. Required.
    :return: the requested item, or Not Found if it was not found.
    ---
    summary: A specific folder item.
    tags:
        - heaserver-folders-get-folder-item
    parameters:
        - name: folder_id
          in: path
          required: true
          description: The id of the folder to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A folder id
              value: root
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    item = await request.app[appproperty.HEA_DB].get(request, MONGODB_ITEMS_COLLECTION,
                                                     var_parts=['folder_id', 'id'], sub=request.headers.get(SUB))
    _logger.debug('got from mongo: %s', item)
    run_time_doc: Optional[Dict[str, Any]] = None
    if item is not None:
        wstl_builder = request[requestproperty.HEA_WSTL_BUILDER]
        wstl_builder.data = [item]
        wstl_builder.href = request.url
        if await _add_actual_object(request, wstl_builder, item, headers={SUB: request.headers.get(SUB)}):
            run_time_doc = wstl_builder()
        else:
            run_time_doc = None
    _logger.debug('got from service: %s', run_time_doc)
    return await response.get_from_wstl(request, run_time_doc)


@routes.get('/folders/{folder_id}/items/{id}/opener')
async def get_item_opener(request: web.Request) -> web.Response:
    """
    Opens the requested item.
    :param request: the HTTP request. Required.
    :return: the opened item, or Not Found if the requested item is not openable or does not exist.
    ---
    summary: Folder item opener choices
    tags:
        - heaserver-folders-get-folder-item-open-choices
    parameters:
      - name: folder_id
        in: path
        required: true
        description: The id of the folder.
        schema:
          type: string
        examples:
          example:
            summary: A folder id.
            value: root
      - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    item = await request.app[appproperty.HEA_DB].get(request, MONGODB_ITEMS_COLLECTION,
                                                     var_parts=['folder_id', 'id'], sub=request.headers.get(SUB))
    _logger.debug('got from mongo: %s', item)
    actual_opened: Any = None
    try:
        if item:
            type_name = item.get('actual_object_type_name')
            id_ = item.get('actual_object_id')
            if type_name is not None and id_ is not None:
                url = await type_to_resource_url(request, type_name)
                actual_opened = await client.get_dict(request.app, URL(url) / id_ / 'opener', headers=request.headers)
        _logger.debug('got from service: %s', actual_opened)
        return await response.get(request, actual_opened)
    except ClientResponseError as e:
        return response.status_from_exception(e)


@routes.get('/folders/{id}/opener')
@action('heaserver-folders-folder-open-default', rel='hea-default application/x.folder')
async def get_folder_opener(request: web.Request) -> web.Response:
    """
    Opens the requested folder.
    :param request: the HTTP request. Required.
    :return: the opened folder, or Not Found if the requested item does not exist.
    ---
    summary: Folder opener choices
    tags:
        - heaserver-folders-get-folder-open-choices
    parameters:
      - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.opener(request, MONGODB_FOLDER_COLLECTION)


@routes.get('/folders/{folder_id}/items/{id}/duplicator')
async def get_item_duplicator(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested item.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested item was not found.
    """
    item = await request.app[appproperty.HEA_DB].get(request, MONGODB_ITEMS_COLLECTION,
                                                     var_parts=['folder_id', 'id'], sub=request.headers.get(SUB))
    _logger.debug('got from mongo: %s', item)
    run_time_doc: Optional[Dict[str, Any]] = None
    if item is not None:
        wstl_builder = request[requestproperty.HEA_WSTL_BUILDER]
        wstl_builder.data = [item]
        wstl_builder.href = request.url
        if await _add_actual_object_duplicate_form(request, wstl_builder, item, headers={SUB: request.headers.get(SUB)}):
            run_time_doc = wstl_builder()
        else:
            run_time_doc = None
    _logger.debug('got from service: %s', run_time_doc)
    return await response.get_from_wstl(request, run_time_doc)


@routes.get('/folders/{id}/duplicator')
@action(name='heaserver-folders-folder-duplicate-form', path='/folders/{folder_id}/items/{id}')
async def get_folder_duplicator(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested folder.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested folder was not found.
    """
    return await _get_folder(request)


@routes.post('/folders/{folder_id}/duplicator')
async def post_item_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided item for duplication.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return post_item_in_folder(request)


@routes.get('/folders/{folder_id}/items/{id}/mover')
@action(name='heaserver-folders-item-move-form', path='/folders/{folder_id}/items/{id}', include_root=True)
async def get_item_mover(request: web.Request) -> web.Response:
    """
    Gets a form template for moving the requested item.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested item was not found.
    """
    item = await request.app[appproperty.HEA_DB].get(request, MONGODB_ITEMS_COLLECTION,
                                                     var_parts=['folder_id', 'id'], sub=request.headers.get(SUB))
    return await response.get(request, item)


@routes.post('/folders/{folder_id}/mover')
async def post_item_mover(request: web.Request) -> web.Response:
    """
    Posts the provided item for moving.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return put_item_in_folder(request)


@routes.post('/folders/{folder_id}/items')
@routes.post('/folders/{folder_id}/items/')
async def post_item_in_folder(request: web.Request) -> web.Response:
    """
    Gets the items in the folder with the specified id.
    :param request: the HTTP request. The body of the request is expected to be an item or an actual object.
    :return: the response, with a 204 status code if an item was created or a 400 if not. If an item was created, the
    Location header will contain the URL of the created item.
    """
    user = request.headers.get(SUB)

    #
    #
    # check setter permissions -- FIXME: need to move this to a central location and apply to all associations with other HEAObjects on POST and PUT
    if request.match_info['folder_id'] == ROOT_FOLDER.id:
        folder = ROOT_FOLDER
    else:
        folder = Folder()
        folder_dict = await request.app[HEA_DB].get(request, MONGODB_FOLDER_COLLECTION, var_parts='folder_id', sub=user)
        if folder_dict is None:
            return response.status_not_found()
        folder.from_dict(folder_dict)

    def has_perms(obj_, user_, perms):
        def share_has_perms(share):
            return share.user == user_ and any(perm in perms for perm in share.permissions)

        return any(share_has_perms(share) for share in obj_.shares)

    if has_perms(folder, user, SETTER_PERMS):
        return response.status_bad_request()

    try:
        type_ = request.url.query['type']
        if type_ is None or type_ == Item.get_type_name():
            item = await new_heaobject(request, Item)
            if item.actual_object is None:
                return response.status_bad_request()
            if item.actual_object_id != item.actual_object.id:
                return response.status_bad_request()
            if item.actual_object_type_name != item.actual_object.get_type_name():
                return response.status_bad_request()
            obj = type_for_name(item.actual_object_type_name)
            obj.from_dict(item.actual_object)
            item.actual_object = None
        else:
            obj = await new_heaobject(request, request.url.query['type'])
            item = Item()
            item.actual_object_type_name = obj.get_type_name()
            item.folder_id = request.match_info['folder_id']
        url = await client.post(request.app,
                                await type_to_resource_url(request, item.actual_object_type_name),
                                obj,
                                headers={SUB: request.headers.get(SUB)})
        item.actual_object_id = URL(url).parts[-1]
        result = await request.app[appproperty.HEA_DB].post(request, item, MONGODB_ITEMS_COLLECTION)
        return await response.post(request, result, MONGODB_ITEMS_COLLECTION)
    except ClientResponseError as e:
        return response.status_from_exception(e)
    except DeserializeException as e:
        return response.status_bad_request(str(e))


@routes.put('/folders/{folder_id}/items/{id}/content')
async def put_item_content(request: web.Request) -> web.Response:
    item = await request.app[appproperty.HEA_DB].get(request, MONGODB_ITEMS_COLLECTION,
                                                     var_parts=['folder_id', 'id'], sub=request.headers.get(SUB))
    if item:
        headers = {SUB: request.headers.get(SUB), hdrs.ACCEPT: request.headers.get(hdrs.ACCEPT)}
        type_name = item.get('actual_object_type_name')
        id_ = item.get('actual_object_id')
        if type_name is None or id_ is None:
            return None
        url = await type_to_resource_url(request, type_name)
        if url is None:
            _logger.debug('Type name %s not found in registry', type_name)
            return None
        try:
            await client.put_streaming(request, URL(url) / id_ / 'content', request.content, headers=headers)
            return await response.put(True)
        except ClientResponseError as e:
            return response.status_from_exception(e)
        except OSError:
            pass
    else:
        return response.status_not_found()


@routes.get('/folders/{folder_id}/items/{id}/content')
async def get_item_content(request: web.Request) -> web.Response:
    item = await request.app[appproperty.HEA_DB].get(request, MONGODB_ITEMS_COLLECTION,
                                                     var_parts=['folder_id', 'id'], sub=request.headers.get(SUB))
    if item:
        headers = {SUB: request.headers.get(SUB), hdrs.ACCEPT: request.headers.get(hdrs.ACCEPT)}
        type_name = item.get('actual_object_type_name')
        id_ = item.get('actual_object_id')
        if type_name is None or id_ is None:
            return None
        url = await type_to_resource_url(request, type_name)
        if url is None:
            _logger.debug('Type name %s not found in registry', type_name)
            return None
        try:
            if type_name == Folder.get_type_name():
                return await client.get_streaming(request, URL(url) / request.match_info['folder_id'] / 'items', headers=headers)
            else:
                return await client.get_streaming(request, URL(url) / id_ / 'content', headers=headers)
        except ClientResponseError as e:
            return response.status_from_exception(e)
    else:
        return response.status_not_found()


@routes.put('/folders/{folder_id}/items/{id}')
async def put_item_in_folder(request: web.Request) -> web.Response:
    """
    Updates the item with the specified id.
    :param request: the HTTP request. The body of the request may be an item, optionally with the actual object, or
    just the actual object. If the body contains an item without the actual object, HEA assumes that the item should
    continue to associate with the same actual object as before.
    :return: No Content or Not Found.
    """
    #
    #
    # check setter permissions -- FIXME: need to move this to a central location and apply to all associations with other HEAObjects on POST and PUT
    user = request.headers.get(SUB)

    if request.match_info['folder_id'] == ROOT_FOLDER.id:
        folder = ROOT_FOLDER
    else:
        folder = Folder()
        folder_dict = await request.app[HEA_DB].get(request, MONGODB_FOLDER_COLLECTION, var_parts='folder_id', sub=user)
        _logger.debug('Requested folder %s, found folder %s', request.match_info["folder_id"], folder_dict)
        if folder_dict is None:
            return response.status_not_found()
        folder.from_dict(folder_dict)

    def has_perms(obj_, user_, perms):
        def share_has_perms(share):
            return share.user == user_ and any(perm in perms for perm in share.permissions)

        return any(share_has_perms(share) for share in obj_.shares)

    if has_perms(folder, user, SETTER_PERMS):
        return response.status_bad_request()

    item_dict = await request.app[appproperty.HEA_DB].get(request, MONGODB_ITEMS_COLLECTION,
                                                          var_parts=['folder_id', 'id'])
    if item_dict is None:
        return response.status_not_found()
    url_ = URL(await type_to_resource_url(request, item_dict['actual_object_type_name'])) / item_dict[
        'actual_object_id']
    obj_ = await client.get(request.app, url_, type_for_name(item_dict['actual_object_type_name']))
    if obj_ is None:
        return response.status_not_found()
    try:
        item = await new_heaobject(request, Item)
        if item.actual_object_id != item_dict.get('actual_object_id'):
            return response.status_bad_request()
        if item.actual_object_type_name != item_dict.get('actual_object_type_name'):
            return response.status.bad_request()
        if item.actual_object_id != (item.actual_object.id if item.actual_object is not None else obj_.id):
            return response.status_bad_request()
        if item.actual_object_type_name != (
        item.actual_object.get_type_name() if item.actual_object is not None else obj_.get_type_name()):
            return response.status_bad_request()
        if item.actual_object is not None:
            url = URL(await type_to_resource_url(request, item.actual_object_type_name)) / item.actual_object_id
            await client.put(request.app, url, item.actual_object, headers={SUB: request.headers.get(SUB)})
            item.actual_object = None
        result = await request.app[appproperty.HEA_DB].put(request, item, MONGODB_ITEMS_COLLECTION)
        return await response.put(result)
    except ClientResponseError as e:
        return response.status_from_exception(e)
    except DeserializeException as e:
        return response.status_bad_request(str(e))


@routes.delete('/folders/{folder_id}/items/{id}')
async def delete_item(request: web.Request) -> web.Response:
    """
    Deletes the item with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Folder item deletion
    tags:
        - heaserver-folders-delete-folder-item
    parameters:
        - name: folder_id
          in: path
          required: true
          description: The id of the folder.
          schema:
            type: string
          examples:
            example:
              summary: A folder id
              value: root
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    item = await request.app[appproperty.HEA_DB].get(request, MONGODB_ITEMS_COLLECTION,
                                                     var_parts=['folder_id', 'id'],
                                                     sub=request.headers.get(SUB))
    _logger.debug('Deleting item %s', item)
    if item is None:
        return response.status_not_found()
    url_str = await type_to_resource_url(request, item['actual_object_type_name'])
    if url_str is None:
        return response.status_not_found()
    try:
        await client.delete(request.app, URL(url_str) / item['actual_object_id'], headers={SUB: request.headers.get(SUB)})
    except ClientResponseError as e:
        return response.status_from_exception(e)
    result = await request.app[appproperty.HEA_DB].delete(request, MONGODB_ITEMS_COLLECTION)
    return await response.delete(result)


@routes.post('/folders')
@routes.post('/folders/')
async def post_folder(request: web.Request) -> web.Response:
    """
    Creates a folder.
    :param request: the HTTP request.
    :return: Created.
    """
    return await mongoservicelib.post(request, MONGODB_FOLDER_COLLECTION, Folder)


@routes.put('/folders/{id}')
async def put_folder(request: web.Request) -> web.Response:
    """
    Updates the folder with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    """
    return await mongoservicelib.put(request, MONGODB_FOLDER_COLLECTION, Folder)


@routes.delete('/folders/{id}')
async def delete_folder(request: web.Request) -> web.Response:
    """
    Deletes the folder with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Folder deletion
    tags:
        - heaserver-folders-delete-folder
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.delete(request, MONGODB_FOLDER_COLLECTION)


def main():
    config = init_cmd_line(description='Repository of folders', default_port=8086)
    start(db=mongo.Mongo, wstl_builder_factory=builder_factory(__package__), config=config)


async def _add_actual_object(request: web.Request, wstl_builder: RuntimeWeSTLDocumentBuilder, item: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
    """
    Updates the folder run-time document by setting the item's actual_object property and any actions for the actual
    object.

    :param request: the HTTP request (required).
    :param item: an item dict in the folder run-time document.
    :param wstl_builder: the WeSTL document builder.
    :param headers: optional dict of headers.
    :return: the updated item, or None if item is None or the actual object was not found.
    :raises ClientResponseError: if getting the actual object failed.
    """
    if item:
        type_name = item.get('actual_object_type_name')
        id_ = item.get('actual_object_id')
        if type_name is None or id_ is None:
            return None
        url = await type_to_resource_url(request, type_name)
        if url is None:
            _logger.debug('Type name %s not found in registry', type_name)
            return None
        if headers:
            headers_ = dict(headers)
            headers_.update({SUB: headers_[SUB] if headers_[SUB] else '', hdrs.ACCEPT: wstljson.MIME_TYPE})
        else:
            headers_ = headers
        actual_object_run_time_doc = await client.get_dict(request.app, URL(url) / id_, headers=headers_)
        if actual_object_run_time_doc is None:
            return None
        else:
            item['actual_object'] = next(iter(actual_object_run_time_doc['wstl'].get('data', [])), None)
            if item['actual_object'] is not None:
                await _add_actions(actual_object_run_time_doc, wstl_builder, request)
            return item
    else:
        return None


async def _add_actions(actual_object_run_time_doc: Dict[str, Any], wstl_builder: RuntimeWeSTLDocumentBuilder, request: web.Request):
    for action in actual_object_run_time_doc['wstl'].get('actions', []):
        if not wstl_builder.has_design_time_action(action['name']):
            wstl_builder.add_design_time_action(action)
        if not wstl_builder.has_run_time_action(action['name']):
            wstl_builder.add_run_time_action(action['name'],
                                             path=action['href'],
                                             root=request.app[appproperty.HEA_COMPONENT],
                                             rel=action.get('rel', None))


async def _add_actual_object_duplicate_form(request: web.Request, wstl_builder: RuntimeWeSTLDocumentBuilder, item: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
    """
    Updates the folder duplicator run-time document with the item's actual_object property set and any actions for the
    actual object.

    :param request: the HTTP request (required).
    :param item: the run-time WeSTL document as a dict.
    :param headers: optional dict of headers.
    :return: the updated item, or None if item is None or the actual object was not found.
    """
    _logger.debug('Making duplicator call for item %s', item)
    if item:
        type_name = item.get('actual_object_type_name')
        id_ = item.get('actual_object_id')
        if type_name is None or id_ is None:
            return None
        url = await type_to_resource_url(request, type_name)
        if headers:
            headers_ = dict(headers)
            headers_.update({SUB: headers_[SUB], hdrs.ACCEPT: wstljson.MIME_TYPE})
        else:
            headers_ = headers
        actual_object_run_time_doc = await client.get_dict(request.app, URL(url) / id_ / 'duplicator',
                                                           headers=headers_)
        if actual_object_run_time_doc is None:
            return None
        else:
            item['actual_object'] = next(iter(actual_object_run_time_doc['wstl'].get('data', [])), None)
            if item['actual_object'] is not None:
                await _add_actions(actual_object_run_time_doc, wstl_builder, request)
            return item
    else:
        return None
