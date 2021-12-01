from heaserver.service.runner import init, routes, start, init_cmd_line
from heaserver.service.db import mongo, mongoservicelib
from heaserver.service.wstl import builder_factory, action
from heaobject.dataadapter import DataAdapter
from aiohttp import web
import logging

_logger = logging.getLogger(__name__)

MONGO_DATA_ADAPTER_COLLECTION = 'dataadapters'


@routes.get('/dataadapters/{id}')
@action('heaserver-data-adapters-data-adapter-get-properties', rel='properties')
@action('heaserver-data-adapters-data-adapter-duplicate', rel='duplicator', path='/dataadapters/{id}/duplicator')
async def get_data_adapter(request:  web.Request) -> web.Response:
    """
    Gets the data adapter with the specified id.
    :param request: the HTTP request.
    :return: the requested data adapter or Not Found.
    ---
    summary: A specific data adapter.
    tags:
        - dataadapters
    parameters:
        - name: id
          in: path
          required: true
          description: The id of the data adapter to retrieve.
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
    return await mongoservicelib.get(request, MONGO_DATA_ADAPTER_COLLECTION)


@routes.get('/dataadapters/byname/{name}')
async def get_data_adapter_by_name(request: web.Request) -> web.Response:
    """
    Gets the data adapter with the specified id.
    :param request: the HTTP request.
    :return: the requested data adapter or Not Found.
    """
    return await mongoservicelib.get_by_name(request, MONGO_DATA_ADAPTER_COLLECTION)



@routes.get('/dataadapters')
@routes.get('/dataadapters/')
@action('heaserver-data-adapters-data-adapter-get-properties', rel='properties')
@action('heaserver-data-adapters-data-adapter-duplicate', rel='duplicator', path='/dataadapters/{id}/duplicator')
async def get_all_data_adapters(request: web.Request) -> web.Response:
    """
    Gets all data adapters.
    :param request: the HTTP request.
    :return: all data adapters.
    """
    return await mongoservicelib.get_all(request, MONGO_DATA_ADAPTER_COLLECTION)


@routes.get('/dataadapters/{id}/duplicator')
@action(name='heaserver-data-adapters-data-adapter-duplicate-form')
async def get_data_adapter_duplicator(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested data adapter.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested data adapter was not found.
    """
    return await mongoservicelib.get(request, MONGO_DATA_ADAPTER_COLLECTION)


@routes.post('/dataadapters/{id}/duplicator')
async def post_data_adapter_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided data adapter for duplication.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return await mongoservicelib.post(request, MONGO_DATA_ADAPTER_COLLECTION, DataAdapter)

@routes.post('/dataadapters')
@routes.post('/dataadapters/')
async def post_data_adapter(request: web.Request) -> web.Response:
    """
    Posts the provided data adapter.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return await mongoservicelib.post(request, MONGO_DATA_ADAPTER_COLLECTION, DataAdapter)


@routes.put('/dataadapters/{id}')
async def put_data_adapter(request: web.Request) -> web.Response:
    """
    Updates the data adapter with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
    """
    return await mongoservicelib.put(request, MONGO_DATA_ADAPTER_COLLECTION, DataAdapter)


@routes.delete('/dataadapters/{id}')
async def delete_component(request: web.Request) -> web.Response:
    """
    Deletes the data adapter with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    """
    return await mongoservicelib.delete(request, MONGO_DATA_ADAPTER_COLLECTION)


def main():
    config = init_cmd_line(description='Data adapters for accessing data sources', default_port=8082)
    start(db=mongo.Mongo, wstl_builder_factory=builder_factory(__package__), config=config)
