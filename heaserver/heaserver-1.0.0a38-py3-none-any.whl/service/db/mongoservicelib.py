import logging

from ..appproperty import HEA_DB
from .. import response, client
from ..heaobjectsupport import new_heaobject, type_to_resource_url
from ..aiohttp import StreamReaderWrapper
from ..oidcclaimhdrs import SUB
from .mongo import Mongo
from heaobject.error import DeserializeException
from heaobject.keychain import Credentials
from heaobject.volume import FileSystem, MongoDBFileSystem, Volume
from aiohttp.web import Request, Response
from typing import Type, IO, Optional, Union, Tuple, Mapping
from heaobject.root import HEAObject
from yarl import URL


async def get(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Gets the HEA object with the specified id.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response with the requested HEA object or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.get(request, collection, var_parts='id')
    return await response.get(request, result)


async def get_content(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Gets the HEA object's associated content.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response with the requested HEA object or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    out = await mongo.get_content(request, collection, var_parts='id')
    if out is not None:
        return await response.get_streaming(request, StreamReaderWrapper(out), 'text/plain')
    else:
        return response.status_not_found()


async def get_by_name(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Gets the HEA object with the specified name.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response with the requested HEA object or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.get(request, collection, var_parts='name')
    return await response.get(request, result)


async def get_all(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Gets all HEA objects.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response with a list of HEA object dicts.
    """
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.get_all(request, collection)
    return await response.get_all(request, result)


async def opener(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Gets choices for opening an HEA desktop object's content.

    :param request: the HTTP request. Required. If an Accepts header is provided, MIME types that do not support links
    will be ignored.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response object with status code 300, and a body containing the HEA desktop object and links
    representing possible choices for opening the HEA desktop object; or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.get(request, collection, var_parts='id')
    return await response.get_multiple_choices(request, result)


async def post(request: Request, collection: str, type_: Type[HEAObject], default_content: Optional[IO] = None, volume_id: Optional[str] = None) -> Response:
    """
    Posts the provided HEA object.

    :param request: the HTTP request.
    :param collection: the Mongo collection name. Required.
    :param type_: The HEA object type. Required.
    :param default_content: an optional blank document or other default content as a file-like object. This must be not-None
    for any microservices that manage content.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response object with a status of Created and the object's URI in the
    """
    try:
        obj = await new_heaobject(request, type_)
        mongo = await _get_mongo(request, volume_id)
        result = await mongo.post(request, obj, collection, default_content)
        return await response.post(request, result, collection)
    except DeserializeException:
        return response.status_bad_request()


async def put(request: Request, collection: str, type_: Type[HEAObject], volume_id: Optional[str] = None) -> Response:
    """
    Updates the HEA object with the specified id.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param type_: The HEA object type. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response object with a status of No Content or Not Found.
    """
    try:
        obj = await new_heaobject(request, type_)
        if request.match_info['id'] != obj.id:
            return response.status_bad_request()
        mongo = await _get_mongo(request, volume_id)
        result = await mongo.put(request, obj, collection)
        return await response.put(result.matched_count if result else False)
    except DeserializeException:
        return response.status_bad_request()


async def put_content(request: Request, collection: str, type_: Type[HEAObject], volume_id: Optional[str] = None) -> Response:
    """
    Updates the HEA object's associated content.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param type_: The HEA object type. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: a Response object with a status of No Content or Not Found.
    """
    try:
        mongo = await _get_mongo(request, volume_id)
        result = await mongo.put_content(request, collection)
        return await response.put(result)
    except DeserializeException:
        return response.status_bad_request()


async def delete(request: Request, collection: str, volume_id: Optional[str] = None) -> Response:
    """
    Deletes the HEA object with the specified id and any associated content.

    :param request: the HTTP request. Required.
    :param collection: the Mongo collection name. Required.
    :param volume_id: the id string of the volume containing the requested HEA object. If None, the root volume is
    assumed.
    :return: No Content or Not Found.
    """
    mongo = await _get_mongo(request, volume_id)
    result = await mongo.delete(request, collection)
    return await response.delete(result.deleted_count if result else False)


async def _get_mongo(request: Request, volume_id: Optional[str]) -> Mongo:
    """
    Gets a mongo client.

    :param request: the HTTP request (required).
    :param volume_id: the id string of a volume.
    :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
    was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
    application-level property.
    :raise ValueError: if there is no volume with the provided volume id.
    """
    headers = {SUB: request.headers.get(SUB)} if SUB in request.headers else None
    volume, volume_url = await _get_volume(request, volume_id, headers)
    if volume is not None and volume.file_system_name is not None:
        fs_url = await type_to_resource_url(request, FileSystem)
        file_system = await client.get(request.app, URL(fs_url) / volume.file_system_name, MongoDBFileSystem, headers=headers)
        credential = await _get_credential(request, volume, volume_url, headers)
        if credential is None:
            return Mongo(connection_string=file_system.connection_string)
        else:
            return Mongo(connection_string=file_system.connection_string, username=credential.account, password=credential.password)
    else:
        return request.app[HEA_DB]


async def _get_volume(request: Request, volume_id: Optional[str], headers: Optional[Mapping] = None) -> Union[Tuple[Volume, Union[str, URL]], Tuple[type(None), type(None)]]:
    """
    Gets the volume with the provided id.

    :param request: the HTTP request (required).
    :param volume_id: the id string of a volume.
    :param headers: any headers.
    :return: a two-tuple with either the Volume and its URL, or (None, None).
    :raise ValueError: if there is no volume with the provided volume id.
    """
    if volume_id is not None:
        volume_url = await type_to_resource_url(request, Volume)
        volume = await client.get(request.app, Volume, URL(volume_url) / volume_id, Volume, headers=headers)
        if volume is None:
            raise ValueError(f'No volume with volume_id={volume_id}')
        return volume, volume_url
    else:
        return None, None


async def _get_credential(request: Request, volume: Volume, volume_url: Union[str, URL], headers: Optional[Mapping] = None) -> Optional[Credentials]:
    """
    Gets a credential specified in the provided volume, or if there is none, a credential with its where attribute set
    to the volume's URL.

    :param request: the HTTP request (required).
    :param volume: the Volume (required).
    :param volume_url: the volume's URL (required).
    :param headers: any headers.
    :return: the Credentials, or None if no credentials were found.
    """
    cred_url = await type_to_resource_url(request, Credentials)
    if volume.credentials_id is not None:
        credential = await client.get(request.app, URL(cred_url) / volume.credential_id, Credentials, headers=headers)
        if credential is not None:
            return credential
    return next(
        await client.get(request.app, URL(cred_url).with_query({'where': volume_url}), headers=headers), None)
