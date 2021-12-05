from kafka_processor.kafka_processor_consumer import KafkaProcessorConsumer
from tests.mockers.kafka import MockedKafka
from unittest.mock import patch
import pytest


@pytest.fixture
def kafka_consumer(stop_instance_after_test_ends):
    with patch("kafka_processor.kafka_processor_consumer.KafkaConsumer", MockedKafka):
        kafka_processor_consumer = KafkaProcessorConsumer.start("test_group_id", bootstrap_servers="test_cluster")

    consumer = kafka_processor_consumer._consumer
    consumer.set_messages_to_topic("test_topic", 0, ["msg_1", "msg_2"])
    stop_instance_after_test_ends(kafka_processor_consumer)

    return kafka_processor_consumer


@pytest.fixture
def stop_instance_after_test_ends():
    items_to_stop = []

    yield items_to_stop.append

    for item in items_to_stop:
        item.stop()


SINGLE_TOPIC_SINGLE_PARTITION = (("test_topic_a",), (0,), (["msg_1", "msg_2"],))
SINGLE_TOPIC_MULTI_PARTITION = (("test_topic_a", "test_topic_a"), (0, 1), (["msg_1"], ["msg_2"]))
MULTI_TOPIC_SINGLE_PARTITION = (("test_topic_a", "test_topic_b"), (0, 0), (["msg_1"], ["msg_2"]))
MULTI_TOPIC_MULTI_PARTITION = (("test_topic_a", "test_topic_b"), (0, 1), (["msg_1"], ["msg_2"]))


@pytest.fixture(params=[SINGLE_TOPIC_SINGLE_PARTITION, SINGLE_TOPIC_MULTI_PARTITION,
                        MULTI_TOPIC_SINGLE_PARTITION, MULTI_TOPIC_MULTI_PARTITION])
def kafka_consumer_with_messages(kafka_consumer, request):
    for topic_name, partition, messages in zip(*request.param):
        kafka_consumer._consumer.set_messages_to_topic(topic_name, partition, messages)

    return kafka_consumer


def test_init_consumer():

    consumer = KafkaProcessorConsumer("consumer", "consumer_metrics")

    assert consumer._consumer == "consumer", (
        f"wrong value set for '_consumer', expected: 'consumer' found: {consumer._consumer}")
    assert isinstance(consumer._topics, set), (
        f"wrong value was set for '_topics', expected: set, found: {type(consumer._topics)}"
    )
    assert consumer.consumer_metrics == "consumer_metrics", (
        f"wrong value set for '_metrics', expected: 'some_metrics' found: {consumer.consumer_metrics}"
    )


@patch("kafka_processor.kafka_processor_consumer.KafkaConsumer", MockedKafka)
def test_start_consumer(stop_instance_after_test_ends):
    processor = KafkaProcessorConsumer.start("test_group_id")
    stop_instance_after_test_ends(processor)

    consumer = processor._consumer

    assert consumer.group_id == "test_group_id", (
        f"consumer was initialized with wrong value for 'group_id', expected: test_group_id, found: {consumer.group_id}"
    )

    assert not consumer.enable_auto_commit, (
        f"consumer was initialized with wrong value for 'enable_auto_commit', "
        f"expected: False, found: {consumer.enable_auto_commit}"
    )


def test_follow_topic(kafka_consumer):
    kafka_consumer.follow_topic("test_topic")

    assert "test_topic" in kafka_consumer._consumer.subscribed, "topic 'test_topic' was not subscribed in kafka"
    assert "test_topic" in kafka_consumer._topics, "topic 'test_topic' was not subscribed in kafka processor consumer"


def test_follow_topic_missing_topic(kafka_consumer, caplog):

    kafka_consumer.follow_topic("missing_topic")

    assert "missing_topic" in kafka_consumer._consumer.subscribed, (
        "topic 'missing_topic' was not subscribed in kafka client"
    )
    assert "missing_topic" in kafka_consumer._topics, (
        "topic 'missing_topic' was not subscribed in kafka processor consumer"
    )

    assert any(record.levelname == "WARNING" and "topic 'missing_topic' not found on cluster" in record.message
               for record in caplog.records), "missing warning log message on about the missing topic"


def test_unfollow_topic(kafka_consumer):
    kafka_consumer.unfollow_topic("test_topic")

    assert "test_topic" not in kafka_consumer._topics, (
        "topic 'test_topic' was not removed from  kafka processor consumer"
    )

    assert "test_topic" not in kafka_consumer._consumer.subscribed, (
        "topic 'test_topic' was not remove from kafka client"
    )


def test_unfollow_topic_no_followed(kafka_consumer):
    kafka_consumer.unfollow_topic("missing_topic")

    assert "missing_topic" not in kafka_consumer._topics, (
        "topic 'missing_topic' was not removed from  kafka processor consumer"
    )

    assert "missing_topic" not in kafka_consumer._consumer.subscribed, (
        "topic 'missing_topic' was not remove from kafka client"
    )


def test_commit_offset(kafka_consumer):
    kafka_consumer.commit(5, "test_topic", 0)

    consumer = kafka_consumer._consumer
    topic_partition = consumer.get_topic_partition("test_topic", 0)

    assert consumer.committed(topic_partition) == 5


def test_read_messages(kafka_consumer_with_messages):
    messages_count = 0

    for topic, messages in kafka_consumer_with_messages.read().items():
        messages_count += len(messages)

    assert messages_count == 4
