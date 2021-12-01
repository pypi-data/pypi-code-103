"""
The HEA Server Organization provides ...
"""

from heaserver.service import response, appproperty
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import mongo, mongoservicelib
from heaserver.service.wstl import builder_factory, action
from heaobject.organization import Organization
import logging
import copy

_logger = logging.getLogger(__name__)

MONGODB_ORGANIZATION_COLLECTION = 'organizations'


@routes.get('/organizations/{id}')
@action('heaserver-organizations-organization-get-properties', rel='properties')
@action('heaserver-organizations-organization-get-open-choices', rel='hea-opener-choices', path='/organizations/{id}/opener')
@action('heaserver-organizations-organization-duplicate', rel='duplicator', path='/organizations/{id}/duplicator')
async def get_organization(request: web.Request) -> web.Response:
    """
    Gets the organization with the specified id.
    :param request: the HTTP request.
    :return: the requested organization or Not Found.
    ---
    summary: A specific organization.
    tags:
        - organizations
    parameters:
        - name: id
          in: path
          required: true
          description: The id of the organization to retrieve.
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
    #todo 'user = request.headers.get(SUB)' need find if lab belongs to user or they apart of
    #todo not sure if at this point we initalize the session for aws
    _logger.debug('Requested organization by id %s' % request.match_info["id"])
    return await mongoservicelib.get(request, MONGODB_ORGANIZATION_COLLECTION)


@routes.get('/organizations/byname/{name}')
async def get_organization_by_name(request: web.Request) -> web.Response:
    """
    Gets the organization with the specified id.
    :param request: the HTTP request.
    :return: the requested organization or Not Found.
    ---
    summary: get a specific organization by name.
    tags:
        - organizations
    parameters:
        - name: name
          in: path
          required: true
          description: The name of the organization to retrieve.
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
    return await mongoservicelib.get_by_name(request, MONGODB_ORGANIZATION_COLLECTION)


@routes.get('/organizations')
@routes.get('/organizations/')
@action('heaserver-organizations-organization-get-properties', rel='properties')
@action('heaserver-organizations-organization-get-open-choices', rel='hea-opener-choices', path='/organizations/{id}/opener')
@action('heaserver-organizations-organization-duplicate', rel='duplicator', path='/organizations/{id}/duplicator')
async def get_all_organizations(request: web.Request) -> web.Response:
    """
    Gets all organizations.
    :param request: the HTTP request.
    :return: all organizations.
    """
    return await mongoservicelib.get_all(request, MONGODB_ORGANIZATION_COLLECTION)


@routes.get('/organizations/{id}/duplicator')
@action(name='heaserver-organizations-organization-duplicate-form', path='/organizations/{id}')
async def get_organization_duplicate_form(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested organization.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested organization was not found.
    """
    return await mongoservicelib.get(request, MONGODB_ORGANIZATION_COLLECTION)


@routes.post('/organization/duplicator')
async def post_organization_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided organization for duplication.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return await mongoservicelib.post(request, MONGODB_ORGANIZATION_COLLECTION, Organization)


@routes.post('/organizations')
@routes.post('/organizations/')
async def post_organization(request: web.Request) -> web.Response:
    """
    Posts the provided organization.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return await mongoservicelib.post(request, MONGODB_ORGANIZATION_COLLECTION, Organization)


@routes.put('/organizations/{id}')
async def put_organization(request: web.Request) -> web.Response:
    """
    Updates the organization with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
    """
    return await mongoservicelib.put(request, MONGODB_ORGANIZATION_COLLECTION, Organization)


@routes.delete('/organizations/{id}')
async def delete_organization(request: web.Request) -> web.Response:
    """
    Deletes the organization with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    """
    return await mongoservicelib.delete(request, MONGODB_ORGANIZATION_COLLECTION)


@routes.get('/organizations/{id}/opener')
async def get_organization_opener(request: web.Request) -> web.Response:
    """

    :param request:
    :return:
    ---
    summary: Organization opener choices
    tags:
        - heaserver-organizations-organization-get-open-choices
    parameters:
        - name: id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
    responses:
      '300':
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
        description: Response if the organization was not found.
    """
    return await mongoservicelib.opener(request, MONGODB_ORGANIZATION_COLLECTION)


def main() -> None:
    config = init_cmd_line(description='a service for managing organization information for research laboratories and other research groups',
                           default_port=8087)
    start(db=mongo.Mongo, wstl_builder_factory=builder_factory(__package__), config=config)
