import os
import logging
from cachetools import TTLCache
from injector import singleton as singleton_scope, provider

from ..providers.base_provider import BaseModule

logger = logging.getLogger(__name__)


class InMemoryTTLCacheDependencyProvider(BaseModule):

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        maxsize: int = int(os.environ.get(
            'ASSUME_ROLE_CACHE_MAX_SIZE',
            '16'
        ))
        ttl: int = int(os.environ.get(
            'ASSUME_ROLE_CACHE_TTL_SECONDS',
            '900'  # 15 minutes
        ))

        if not os.environ.get('DISABLE_CACHE', None):
            logger.info("Created TTL Cache")
            self.session = TTLCache(maxsize=maxsize, ttl=ttl)
        else:
            logger.warning("TTL Cache is disabled")
            self.session = None

    @singleton_scope
    @provider
    def ttl_cache(self) -> TTLCache:
        return self.session