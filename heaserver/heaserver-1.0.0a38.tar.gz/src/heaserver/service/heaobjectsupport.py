"""
Convenience functions for handling HEAObjects.
"""

from . import client
from .representor import factory as representor_factory
from .representor.error import ParseException
from heaobject import root
from heaobject.volume import DEFAULT_FILE_SYSTEM
from heaobject.error import DeserializeException
from heaobject.root import HEAObject
from aiohttp import web
import logging
from typing import Union, Callable, Optional, Type


async def new_heaobject(request: web.Request, type_or_type_name: Union[Callable[[], HEAObject], str]) -> HEAObject:
    """
    Creates a new HEA object from the body of a HTTP request.
    :param request: the HTTP request.
    :param type_or_type_name: the type name of HEAObject, or a callable that returns a HEAObject.
    :return: an instance of the given HEAObject type.
    :raises DeserializeException: if creating a HEA object from the request body's contents failed.
    """
    _logger = logging.getLogger(__name__)
    if isinstance(type_or_type_name, str):
        return await populate_heaobject(request, root.type_for_name(type_or_type_name)())
    else:
        return await populate_heaobject(request, type_or_type_name())


async def populate_heaobject(request: web.Request, obj: HEAObject) -> HEAObject:
    """
    Populate an HEAObject from a POST or PUT HTTP request.

    :param request: the HTTP request. Required.
    :param obj: the HEAObject instance. Required.
    :return: the populated object.
    :raises DeserializeException: if creating a HEA object from the request body's contents failed.
    """
    _logger = logging.getLogger(__name__)
    try:
        representor = representor_factory.from_content_type_header(request.headers['Content-Type'])
        _logger.debug('Using %s input parser', representor)
        result = await representor.parse(request)
        _logger.debug('Got dict %s', result)
        obj.from_dict(result)
        return obj
    except (ParseException, ValueError) as e:
        _logger.exception('Failed to parse %s%s', obj, e)
        raise DeserializeException from e
    except Exception as e:
        _logger.exception('Got exception %s', e)
        raise DeserializeException from e


async def type_to_resource_url(request: web.Request, type_or_type_name: Union[str, Type[HEAObject]],
                               file_system_name: Optional[str] = DEFAULT_FILE_SYSTEM) -> Optional[str]:
    """
    Use the HEA registry service to get the resource URL for accessing HEA objects of the given type.

    :param request: the HTTP request. Required.
    :param type_or_type_name: the type name of HEAObject. Required.
    :param file_system_name: the name of a file system. The default is filesystems.DEFAULT.
    :return: the URL string, or None if no resource URL was found.
    """
    if file_system_name is None:
        file_system_name_ = DEFAULT_FILE_SYSTEM
    else:
        file_system_name_ = file_system_name
    if isinstance(type_or_type_name, str):
        type_ = root.type_for_name(type_or_type_name)
    else:
        type_ = type_or_type_name
    return await client.get_resource_url(request.app, type_, file_system_name_)
