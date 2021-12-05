"""Declares request handlers for liveness and readyness
checks.
"""
from .nocacheresponse import NoCacheResponse


async def ready() -> NoCacheResponse:
    """Perform a readyness check and set status code ``204``
    on the HTTP response if the application is ready,
    else ``503``.
    """
    return NoCacheResponse(content={'status': "OK"})


async def live() -> NoCacheResponse:
    """Perform a liveness check and set status code ``204``
    on the HTTP response if the application is live,
    else ``503``.
    """
    return NoCacheResponse(content={'status': "OK"})
