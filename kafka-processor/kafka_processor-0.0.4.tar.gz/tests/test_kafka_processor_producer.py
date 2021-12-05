from kafka_processor.kafka_processor_producer import KafkaProcessorProducer
from unittest.mock import patch
from tests.mockers.kafka import MockedKafka
from kafka.future import Future
import logging
import pytest


@pytest.fixture
def kafka_producer():
    with patch("kafka_processor.kafka_processor_producer.KafkaProducer", MockedKafka):
        instance = KafkaProcessorProducer.start(bootstrap_servers="test.url")
        yield instance

    instance.stop()


@pytest.fixture
def stop_instance_after_test_ends():
    items_to_stop = []

    yield items_to_stop.append

    for item in items_to_stop:
        item.stop()


def test_init_producer():
    producer = KafkaProcessorProducer("producer", "producer_metrics")

    assert producer._producer == "producer", (
        f"wrong value was set as producer, expected 'producer', found {producer._producer}"
    )

    assert producer.producer_metrics == "producer_metrics", (
        f"wrong value was set as producer_metrics, expected 'producer_metrics', found {producer.producer_metrics}"
    )


@patch("kafka_processor.kafka_processor_producer.KafkaProducer", MockedKafka)
def test_start_producer(stop_instance_after_test_ends):

    kafka_processor_producer = KafkaProcessorProducer.start(bootstrap_servers="test.url")
    stop_instance_after_test_ends(kafka_processor_producer)

    found_bootstrap_servers = kafka_processor_producer._producer.bootstrap_servers

    assert found_bootstrap_servers == "test.url", (
        f"kafka producer wasn't initilized with the right values, "
        f"expected 'bootstrap_servers: test.url' found 'bootstrap_servers: {found_bootstrap_servers}"
    )


def test_send_message_blocking(kafka_producer, caplog):
    caplog.set_level(logging.DEBUG)
    kafka_producer.send("test_topic", "test_key", "test_value", is_blocking=True)

    producer = kafka_producer._producer

    assert producer.last_sent_topic == "test_topic", (
        f"message sent on the wrong topic, expected 'test_topic', found: {kafka_producer.last_sent_topic}"
    )

    sent_key, sent_value = producer.last_sent_message
    assert producer.last_sent_message == ("test_key", "test_value"), (
        f"wrong values were sent, expected '(key:test_key, value:test_value)', "
        f"found: '(key:{sent_key}, value:{sent_value})'"
    )

    assert any(record.levelname == "DEBUG" and "message key 'test_key' was sent to topic 'test_topic'" in record.message
               for record in caplog.records), "missing log message on successfully sending"


def test_send_message_non_blocking(kafka_producer):
    result = kafka_producer.send("test_topic", "test_key", "test_value", is_blocking=False)

    producer = kafka_producer._producer

    assert producer.last_sent_topic == "test_topic", (
        f"message sent on the wrong topic, expected 'test_topic', found: {kafka_producer.last_sent_topic}"
    )

    sent_key, sent_value = producer.last_sent_message

    assert producer.last_sent_message == ("test_key", "test_value"), (
        f"wrong values were sent, expected '(key:test_key, value:test_value)', "
        f"found: '(key:{sent_key}, value:{sent_value})'"
    )

    assert isinstance(result, Future), "wrong value was returned"
