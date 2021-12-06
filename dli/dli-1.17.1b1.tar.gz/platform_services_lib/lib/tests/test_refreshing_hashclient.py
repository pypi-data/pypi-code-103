from pymemcache.client.hash import HashClient
from unittest.mock import MagicMock
import datetime
from freezegun import freeze_time

from lib.providers.memcache_provider import MemcachedDependencyProvider

class TestRefreshingHashClient:

    def test__rediscover_and_recreate_client_on_new_config_is_called(self):
        provider = MemcachedDependencyProvider(
            elasticache_config_node_url='test:8000',
            default_ttl=36
            )
        test_client = provider.memcached_client()

        def rediscover_side_effect():
            test_client._last_successful_discovery = datetime.datetime.now()
            test_client._client = MagicMock()

        test_client._rediscover_and_recreate_client_on_new_config = MagicMock(side_effect=rediscover_side_effect)
        test_client.get('h')
        assert test_client._client is not None
        old_magic_mock = test_client._client

        test_client.get('h')
        assert test_client._client is old_magic_mock
        deltatime = test_client._last_successful_discovery + datetime.timedelta(minutes=6)
        with freeze_time(deltatime):
            test_client.get('h')
            assert test_client._client is not old_magic_mock
            assert test_client._client is not None

    def test_should_rediscover(self):
        provider = MemcachedDependencyProvider(
            elasticache_config_node_url='test:8000',
            default_ttl=36
        )
        test_client = provider.memcached_client()
        test_client._last_successful_discovery = datetime.datetime.now()
        assert test_client._should_rediscover() is False

        deltatime = test_client._last_successful_discovery + datetime.timedelta(minutes=6)
        with freeze_time(deltatime):
            assert test_client._should_rediscover() is True

    def test_rediscover_nodes_sets_client_to_hash_client(self):
        provider = MemcachedDependencyProvider(
            elasticache_config_node_url='test:8000',
            default_ttl=36
            )
        test_client = provider.memcached_client()
        test_client._discover_nodes = MagicMock(return_value=['127.0.0.1'])
        test_client._rediscover_and_recreate_client_on_new_config()
        assert test_client._client is not None and isinstance(test_client._client, HashClient)

    def test_client_set_if_no_nodes_returned(self):
        provider = MemcachedDependencyProvider(
            elasticache_config_node_url='test:8000',
            default_ttl=36
        )
        test_client = provider.memcached_client()
        test_client._discover_nodes = MagicMock(return_value=[])
        test_client._rediscover_and_recreate_client_on_new_config()
        assert test_client._client is None
