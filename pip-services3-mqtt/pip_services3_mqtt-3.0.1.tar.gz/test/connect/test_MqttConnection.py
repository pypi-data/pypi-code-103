# -*- coding: utf-8 -*-
import os

from pip_services3_commons.config import ConfigParams

from pip_services3_mqtt.connect.MqttConnection import MqttConnection


class TestMqttConnection:
    connection: MqttConnection = None

    broker_host = os.environ.get('MQTT_SERVICE_HOST') or 'localhost'
    broker_port = os.environ.get('MQTT_SERVICE_PORT') or 1883

    broker_topic = os.environ.get('MQTT_TOPIC') or 'test'
    broker_user = os.environ.get('MQTT_USER')
    broker_pass = os.environ.get('MQTT_PASS')
    broker_token = os.environ.get('MQTT_TOKEN')

    def setup_method(self):
        config = ConfigParams.from_tuples(
            'topic', self.broker_topic,
            'connection.protocol', 'mqtt',
            'connection.host', self.broker_host,
            'connection.port', self.broker_port,
            'credential.username', self.broker_port,
            'credential.password', self.broker_pass,
            'credential.token', self.broker_token,
        )

        self.connection = MqttConnection()
        self.connection.configure(config)

    def test_open_close(self):
        self.connection.open(None)
        assert self.connection.is_open() is True
        assert self.connection.get_connection() is not None

        self.connection.close(None)
        assert self.connection.is_open() is False
        assert self.connection.get_connection() is None
