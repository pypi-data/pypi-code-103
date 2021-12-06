#  #
#  Copyright (C) 2020 IHS Markit.
#  All Rights Reserved
#  #
#

import logging
import socket
import os
import elasticache_auto_discovery
from pymemcache.client.hash import HashClient
from datetime import datetime, timedelta
from pymemcache import serde


logger = logging.getLogger(__name__)


def get_or_refresh_hashclient(func):
    def wrapper(self, *args, **kwargs):
        if not self._client or self._should_rediscover():
            self._rediscover_and_recreate_client_on_new_config()
        return func(self, *args, **kwargs)
    return wrapper


class RefreshingHashClient:
    def __init__(self, config):
        self.config = config
        self._client = None
        self._discovered_nodes = []
        self._last_successful_discovery = datetime.min

    @get_or_refresh_hashclient
    def get(self, key):
        try:
            return self._client.get(key, None)
        finally:
            return None

    @get_or_refresh_hashclient
    def set(self, key, value, expire=0):
        try:
            self._client.set(key, value, expire=expire, noreply=False)
        finally:
            return None

    @get_or_refresh_hashclient
    def delete(self, key):
        try:
            self._client.delete(key, noreply=False)
        finally:
            return None

    def _rediscover_and_recreate_client_on_new_config(self):
        nodes = self._discover_nodes()
        if nodes and nodes != self._discovered_nodes:
            self._discovered_nodes = nodes
            self._client = \
                HashClient(
                    servers=self._discovered_nodes,
                    use_pooling=True,
                    connect_timeout=self.config.time_to_timeout,
                    serde=serde.pickle_serde,
                )

    def _should_rediscover(self):
        return datetime.utcnow() - self._last_successful_discovery > timedelta(
            minutes=5.0
        )

    def _discover_nodes(self):
        # if running local you will not be able to reach EC memcache
        # but you must have a local memcache running (e.g. localhost:11211 - see /etc/memcached.conf)
        # start it with (sudo apt-get install memcached; sudo systemctl start/stop memcached)
        if os.environ.get('LOCAL_MEMCACHE', None):
            logger.warning(f"EC Memcache unreachable, connecting to local memcache {os.environ.get('LOCAL_MEMCACHE')}")
            return [os.environ.get('LOCAL_MEMCACHE').split(":")]

        try:
            nodes = elasticache_auto_discovery.discover(
                self.config.elasticache_config_node_url,
                time_to_timeout=self.config.time_to_timeout
            )
        except socket.timeout as s:

            logger.warning(f"Memcache is disabled because an exception occurred: {s}")
            return None
        except Exception as e:
            logger.warning(f"Memcache is disabled because an exception occurred: {e}")
            return None

        nodes = [
            (ip.decode("utf-8"), int(port)) for _server, ip, port in nodes
        ]

        logger.info(
            'elasticache_auto_discovery nodes',
            extra={
                'nodes': str(nodes),
                'num nodes': len(nodes)
            }
        )
        return nodes
