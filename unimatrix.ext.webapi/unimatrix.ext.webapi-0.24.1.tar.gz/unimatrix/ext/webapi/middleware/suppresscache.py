"""Declares :class:`SupressCacheMiddleware`."""


class SupressCacheMiddleware:
    """ASGI middleware that instructs downstream server to not cache the
    content, unless otherwise specified.
    """
