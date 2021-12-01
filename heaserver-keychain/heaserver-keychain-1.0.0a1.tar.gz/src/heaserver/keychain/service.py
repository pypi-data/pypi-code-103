"""
The HEA Keychain provides ...
"""

from heaserver.service import response, appproperty
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import mongo, mongoservicelib
from heaserver.service.wstl import builder_factory, action
from heaobject.keychain import Credentials
import logging
import copy

_logger = logging.getLogger(__name__)
MONGODB_KEYCHAIN_COLLECTION = 'keychain'


@routes.get('/keychain/{id}')
@action('heaserver-keychain-keychain-get-properties', rel='properties')
@action('heaserver-keychain-keychain-open', rel='opener', path='/keychain/{id}/opener')
@action('heaserver-keychain-keychain-duplicate', rel='duplicator', path='/keychain/{id}/duplicator')
async def get_keychain(request: web.Request) -> web.Response:
    """
    Gets the keychain with the specified id.
    :param request: the HTTP request.
    :return: the requested keychain or Not Found.
    ---
    summary: A specific keychain.
    tags:
        - keychain
    parameters:
        - name: id
          in: path
          required: true
          description: The id of the keychain to retrieve.
          schema:
            type: string
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """
    _logger.debug('Requested keychain by id %s' % request.match_info["id"])
    return await mongoservicelib.get(request, MONGODB_KEYCHAIN_COLLECTION)


@routes.get('/keychain/byname/{name}')
async def get_keychain_by_name(request: web.Request) -> web.Response:
    """
    Gets the keychain with the specified id.
    :param request: the HTTP request.
    :return: the requested keychain or Not Found.
    """
    return await mongoservicelib.get_by_name(request, MONGODB_KEYCHAIN_COLLECTION)


@routes.get('/keychain')
@routes.get('/keychain/')
@action('heaserver-keychain-keychain-get-properties', rel='properties')
@action('heaserver-keychain-keychain-open', rel='opener', path='/keychain/{id}/opener')
@action('heaserver-keychain-keychain-duplicate', rel='duplicator', path='/keychain/{id}/duplicator')
async def get_all_keychain(request: web.Request) -> web.Response:
    """
    Gets all keychain.
    :param request: the HTTP request.
    :return: all keychain.
    """
    return await mongoservicelib.get_all(request, MONGODB_KEYCHAIN_COLLECTION)


@routes.get('/keychain/{id}/duplicator')
@action(name='heaserver-keychain-keychain-duplicate-form')
async def get_keychain_duplicate_form(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested keychain.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested keychain was not found.
    """
    return await mongoservicelib.get(request, MONGODB_KEYCHAIN_COLLECTION)


@routes.post('/keychain/duplicator')
async def post_keychain_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided keychain for duplication.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return await mongoservicelib.post(request, MONGODB_KEYCHAIN_COLLECTION, Credentials)


@routes.post('/keychain')
@routes.post('/keychain/')
async def post_keychain(request: web.Request) -> web.Response:
    """
    Posts the provided keychain.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return await mongoservicelib.post(request, MONGODB_KEYCHAIN_COLLECTION, Credentials)


@routes.put('/keychain/{id}')
async def put_keychain(request: web.Request) -> web.Response:
    """
    Updates the keychain with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
    """
    return await mongoservicelib.put(request, MONGODB_KEYCHAIN_COLLECTION, Credentials)


@routes.delete('/keychain/{id}')
async def delete_keychain(request: web.Request) -> web.Response:
    """
    Deletes the keychain with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    """
    return await mongoservicelib.delete(request, MONGODB_KEYCHAIN_COLLECTION)


def main() -> None:
    config = init_cmd_line(description='a service for managing laboratory/user credentials',
                           default_port=8080)
    start(db=mongo.Mongo, wstl_builder_factory=builder_factory(__package__), config=config)
