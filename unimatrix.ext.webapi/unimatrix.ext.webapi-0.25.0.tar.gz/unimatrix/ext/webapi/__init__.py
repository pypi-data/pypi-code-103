# pylint: skip-file
import sys

import fastapi
import ioc

from .asgi import Application
from .decorators import action
from .exceptions import UpstreamServiceNotAvailable
from .exceptions import UpstreamConnectionFailure
from .keytrustpolicy import KeyTrustPolicy
from .resource import resource
from .resourceendpointset import ResourceEndpointSet
from .resourceendpointset import PublicResourceEndpointSet
from .service import Service


__all__ = [
    'action',
    'limit',
    'offset',
    'resource',
    'Application',
    'EndpointSet',
    'PublicEndpointSet',
    'Service',
    'UpstreamConnectionFailure',
    'UpstreamServiceNotAvailable',
]


EndpointSet = ResourceEndpointSet
PublicEndpointSet = PublicResourceEndpointSet


def inject(name, invoke=False, *args, **kwargs):
    """Injects the named dependency `name` into the :mod:`fastapi`
    dependency resolver.
    """
    async def provide():
        dependency = ioc.require(name)
        if not hasattr(dependency, '__aenter__'):
            yield dependency if not invoke else dependency(*args, **kwargs)
            return
        if invoke:
            dependency = dependency(*args, **kwargs)
        async with dependency:
            yield dependency
    return fastapi.Depends(provide)


def singleton(cls):
    """Class decorator that indicates that a resource is a singleton."""
    cls.singleton = True
    return cls


def policy(tags: list) -> KeyTrustPolicy:
    """Declares a policy for an endpoint to determine which public keys
    it wants to trust.

    Args:
        tags (list): The list of tags that this policy accepts.

    Returns:
        A :class:`KeyTrustPolicy` instance.
    """
    return KeyTrustPolicy(tags)


def offset(default=0):
    """Creates the ``offset`` query parameter for request
    handlers.
    """
    return fastapi.Query(
        default,
        title='offset',
        description=(
            "The number of objects to skip from the beginning "
            "of the result set."
        )
    )


def limit(default=100, limit=None):
    """Creates the ``limit`` query parameter for request
    handlers.
    """
    limit = default * 3
    return fastapi.Query(
        default,
        title='limit',
        description=(
            "Optional limit on the number of objects to include "
            "in the response.\n\n"
            f"The default is {default}, and the maximum is {limit}."
        )
    )
