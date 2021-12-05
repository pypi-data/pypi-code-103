from kafka_processor.kafka_processor import KafkaProcessor
from kafka_processor.kafka_processor_producer import KafkaProcessorProducer
from kafka_processor.kafka_processor_consumer import KafkaProcessorConsumer
from kafka_processor.processing_flow import ProcessingFlow
from unittest.mock import patch
from tests.mockers.kafka import MockedKafka
import threading
import pytest
from time import sleep


@pytest.fixture
def kafka_processor():
    with patch("kafka_processor.kafka_processor_producer.KafkaProducer", MockedKafka):
        with patch("kafka_processor.kafka_processor_consumer.KafkaConsumer", MockedKafka):
            instance = KafkaProcessor.start("test_group", 1, bootstrap_servers="test.broker.url")
            yield instance

    instance.stop()


@pytest.fixture
def kafka_processor_with_flows(kafka_processor):
    def foo(key, value):
        return key, value*2

    def filter_func(collocation):
        ans = []

        for item in collocation:
            if item.value < 10:
                ans.append(item)

        return ans

    kafka_processor.add_flow("input_topic", "output_topic", [foo], filter_func)

    return kafka_processor


@pytest.fixture
def kafka_processor_with_flows_with_filter_exception(kafka_processor):
    def foo(key, value):
        return key, value*2

    def filter_func(collocation):
        ans = []

        for item in collocation:
            if item.value == 8:
                raise Exception("invalid value")
            elif item.value < 10:
                ans.append(item)
        return ans

    kafka_processor.add_flow("input_topic", "output_topic", [foo], filter_func)

    return kafka_processor


@pytest.fixture
def kafka_processor_with_flows_callback_with_exception(kafka_processor):
    def foo(key, value):
        if value == 8:
            raise Exception("wrong value was supplied")
        return key, value*2

    def filter_func(collocation):
        ans = []

        for item in collocation:
            if item.value < 10:
                ans.append(item)
        return ans

    kafka_processor.add_flow("input_topic", "output_topic", [foo], filter_func)

    return kafka_processor


@pytest.fixture
def schedule_stop_after_test_ends():
    items_to_stop = []

    yield items_to_stop.append

    for item in items_to_stop:
        item.stop()


def test_init_kafka_processor():
    processor = KafkaProcessor("consumer", "producer", 10)

    assert processor.producer == "producer", (
        f"wrong value was set for '_producer', expected: 'producer', found: '{processor.producer}'"
    )

    assert processor.consumer == "consumer", (
        f"wrong value was set for '_consumer', expected: 'consumer', found: '{processor.consumer}'"
    )

    assert processor._polling_interval == 10, (
        f"wrong value was set for '_polling_interval', expected: '10', found: {processor._polling_interval}"
    )
    assert processor._flows == {}, f"wrong value was set for '_flows', expected: '{'{}'}', found: {processor._flows}"
    assert processor._thread is None, (
        f"wrong value was set for '_thread', expected: 'None' , found: {processor._thread}"
    )

    assert isinstance(processor._is_started, bool), (
        f"wrong type set for '_is_started', expected: bool, found: {type(processor._is_started)}"
    )

    assert not processor._is_started, (
        f"wrong value was set for '_is_started', expected: 'False', found: {processor._is_started}"
    )


@patch("kafka_processor.kafka_processor_producer.KafkaProducer", MockedKafka)
@patch("kafka_processor.kafka_processor_consumer.KafkaConsumer", MockedKafka)
def test_start_kafka_processor(schedule_stop_after_test_ends):
    processor = KafkaProcessor.start("test_group", 10, bootstrap_servers="test.broker.url")

    schedule_stop_after_test_ends(processor)

    assert isinstance(processor.consumer, KafkaProcessorConsumer), (
        f"wrong type was created for consumer, expected 'KafkaProcessorConsumer', "
        f"found: '{type(processor.consumer)}'"
    )
    assert isinstance(processor.producer, KafkaProcessorProducer), (
        f"wrong type was created for producer, expected 'KafkaProcessorProducer', "
        f"found: '{type(processor.producer)}'"
    )

    assert isinstance(processor._thread, threading.Thread), (
        f"wrong type was set for thread worker, expected: threading.Thread, found: {type(processor._thread)}"
    )
    assert processor._thread.is_alive(), (
        "the worker thread was expected to be started after the start() function is called but it not alive"
    )

    assert processor._is_started, (
        f"the processor instance was expected to be started after the start() function is "
        f"called but _is_started is {processor._is_started}"
    )


def test_add_flow_to_kafka_processor(kafka_processor):
    def foo():
        pass

    def filter_func():
        pass

    kafka_processor.add_flow("input_topic", "output_topic", [foo], filter_func)

    assert "input_topic" in kafka_processor._flows, "the flow wasn't added to the processor"

    flow = kafka_processor._flows["input_topic"]
    expected_flow = ProcessingFlow("input_topic", "output_topic", [foo], filter_func)

    diff = [
        (f"expected: {expected_flow.__dict__[attr]}", f"found: {flow.__dict__.get(attr, None)}")
        for attr in expected_flow.__dict__ if expected_flow.__dict__[attr] != flow.__dict__.get(attr, None)]

    assert not diff, f"the created flow is not the same as the expected one, {diff}"


def test_remove_flow_to_kafka_processor(kafka_processor_with_flows):
    kafka_processor_with_flows.remove_flow("input_topic")

    assert "input_topic" not in kafka_processor_with_flows._flows, (
        "the 'input_topic' flow was not removed from the kafka processor"
    )


def test_work_filter_content(kafka_processor_with_flows):

    kafka_processor_with_flows.consumer._consumer.set_messages_to_topic("input_topic", 0, [7, 8, 9, 10, 11, 12, 13])
    expected_msgs_to_send = 3
    left_time_for_sending_in_seconds = 5

    # wait for 3 messages to be sent at most 5 seconds
    while kafka_processor_with_flows.producer._producer.send_called < expected_msgs_to_send and (
            left_time_for_sending_in_seconds > 0):
        sleep(1)

    assert kafka_processor_with_flows.producer._producer.sent_messages["output_topic"] == [(7, 14), (8, 16), (9, 18)]


def test_work_filter_exception(kafka_processor_with_flows_with_filter_exception):
    kafka_processor_with_flows_with_filter_exception.consumer._consumer.set_messages_to_topic(
        "input_topic", 0, [7, 8, 9, 10, 11, 12, 13])
    expected_msgs_to_send = 2
    left_time_for_sending_in_seconds = 5

    # wait for 2 messages to be sent at most 5 seconds
    while kafka_processor_with_flows_with_filter_exception.producer._producer.send_called < expected_msgs_to_send and (
            left_time_for_sending_in_seconds > 0):
        sleep(1)
    assert kafka_processor_with_flows_with_filter_exception.producer._producer.sent_messages["output_topic"] == [
        (7, 14), (9, 18)]


def test_callback_exception(kafka_processor_with_flows_callback_with_exception):
    kafka_processor_with_flows_callback_with_exception.consumer._consumer.set_messages_to_topic(
        "input_topic", 0, [7, 8, 9, 10, 11, 12, 13])
    expected_msgs_to_send = 2
    left_time_for_sending_in_seconds = 5

    # wait for 2 messages to be sent at most 5 seconds
    while left_time_for_sending_in_seconds > 0 and (
            kafka_processor_with_flows_callback_with_exception.producer._producer.send_called < expected_msgs_to_send
    ):
        sleep(1)
    assert kafka_processor_with_flows_callback_with_exception.producer._producer.sent_messages["output_topic"] == [
        (7, 14), (9, 18)]
