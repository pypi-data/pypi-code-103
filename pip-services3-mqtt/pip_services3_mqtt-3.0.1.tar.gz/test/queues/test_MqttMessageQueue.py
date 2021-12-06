# -*- coding: utf-8 -*-
import os

from pip_services3_commons.config import ConfigParams

from pip_services3_mqtt.queues.MqttMessageQueue import MqttMessageQueue
from test.queues.MessageQueueFixture import MessageQueueFixture


class TestMqttMessageQueue:
    queue: MqttMessageQueue = None
    fixture: MessageQueueFixture = None

    broker_host = os.environ.get('MQTT_SERVICE_HOST') or 'localhost'
    broker_port = os.environ.get('MQTT_SERVICE_PORT') or 1883

    broker_topic = os.environ.get('MQTT_TOPIC') or 'test'

    queue_config = ConfigParams.from_tuples(
        'topic', broker_topic,
        'connection.protocol', 'mqtt',
        'connection.host', broker_host,
        'connection.port', broker_port,
        'options.autosubscribe', True,
        'options.serialize_envelope', True
    )

    def setup_method(self):
        self.queue = MqttMessageQueue()
        self.queue.configure(self.queue_config)

        self.fixture = MessageQueueFixture(self.queue)

        self.queue.open(None)
        self.queue.clear(None)

    def teardown_method(self):
        self.queue.close(None)

    def test_send_and_receive_message(self):
        self.fixture.test_send_receive_message()

    def test_receive_send_message(self):
        self.fixture.test_receive_send_message()

    def test_send_peek_message(self):
        self.fixture.test_send_peek_message()

    def test_peek_no_message(self):
        self.fixture.test_peek_no_message()

    def test_on_message(self):
        self.fixture.test_on_message()
