# -*- coding: utf-8 -*-
from pip_services3_commons.config import ConfigParams

from pip_services3_mqtt.connect.MqttConnectionResolver import MqttConnectionResolver


class TestMqttConnectionResolver:

    def test_single_connection(self):
        resolver = MqttConnectionResolver()
        resolver.configure(ConfigParams.from_tuples(
            "connection.protocol", "mqtt",
            "connection.host", "localhost",
            "connection.port", 1883
        ))

        connection = resolver.resolve(None)
        assert "mqtt://localhost:1883" == connection['uri']
        assert connection.get('username') is None
        assert connection.get('password') is None

    def test_cluster_uri(self):
        resolver = MqttConnectionResolver()
        resolver.configure(ConfigParams.from_tuples(
            "connection.uri", "mqtt://server1:1883",
            "credential.username", "test",
            "credential.password", "pass123"
        ))

        connection = resolver.resolve(None)
        assert connection['uri'] is not None
        assert 'test' == connection['username']
        assert 'pass123' == connection['password']
