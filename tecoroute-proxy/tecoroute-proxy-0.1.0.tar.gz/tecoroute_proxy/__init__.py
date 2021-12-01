"""TODO."""
from logging import DEBUG, basicConfig, getLogger
from os import environ

from ._proxy import Proxy, ProxyRequest

__all__ = [Proxy.__name__, ProxyRequest.__name__]

logger = getLogger(__name__)


def main():
    """TODO."""
    basicConfig()
    logger.level = DEBUG
    proxy = Proxy(
        environ.get("TECOROUTE_PROXY_HOST", "0.0.0.0"),
        int(environ.get("TECOROUTE_PROXY_PORT", 80)),
    )
    proxy.run()
