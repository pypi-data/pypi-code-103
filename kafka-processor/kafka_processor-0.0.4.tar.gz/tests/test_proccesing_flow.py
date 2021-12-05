from kafka_processor.processing_flow import ProcessingFlow
from kafka_processor.exceptions import FailToProcessMessage
from collections import namedtuple
import pytest

KafkaRecord = namedtuple("KafkaRecord", "key value topic")


@pytest.fixture
def processing_flow():

    def callback_a(key, value):
        return key, value*2

    def callback_b(key, value):
        return key, value*3

    def filtering_function(collection):
        return collection[::2]

    return ProcessingFlow("input_topic", "output_topic", [callback_a, callback_b], filtering_function)


@pytest.fixture
def processing_flow_wo_filtering_function():

    def callback_a(key, value):
        return key, value*2

    def callback_b(key, value):
        return key, value*3

    return ProcessingFlow("input_topic", "output_topic", [callback_a, callback_b])


@pytest.fixture
def processing_flow_callback_exception():

    def callback_a(key, value):
        raise Exception("This is an unexpected exception")

    def callback_b(key, value):
        return value, key

    def filtering_function(collection):
        return collection[::2]

    return ProcessingFlow("input_topic", "output_topic", [callback_a, callback_b], filtering_function)


@pytest.fixture
def processing_flow_filter_exception():

    def callback_a(key, value):
        return value, key

    def callback_b(key, value):
        return value, key

    def filtering_function(collection):
        pass_first_iteration = False

        for _ in collection:
            if pass_first_iteration:
                raise Exception("fail to filter collection")
            else:
                pass_first_iteration = True

        return [0]

    return ProcessingFlow("input_topic", "output_topic", [callback_a, callback_b], filtering_function)


def test_init_processing_flow():
    processing_flow = ProcessingFlow("input_topic", "output_topic", "callbacks", "filter_function")

    assert processing_flow.input_topic == "input_topic", (
        f"wrong value was set for attribute 'input_topic', "
        f"expected:  'input_topic', found: {processing_flow.input_topic}"
    )
    assert processing_flow.output_topic == "output_topic", (
        f"wrong value was set for attribute 'output_topic', "
        f"expected:  'output_topic', found: {processing_flow.output_topic}"
    )
    assert processing_flow.callbacks == "callbacks", (
        f"wrong value was set for attribute 'callbacks', "
        f"expected:  'callbacks', found: {processing_flow.callbacks}"
    )

    assert processing_flow.filter_function == "filter_function", (
        f"wrong value was set for attribute 'filter_function', "
        f"expected:  'filter_function', found: {processing_flow.filter_function}"
    )


def test_filter_processing_flow(processing_flow):
    failed_idx, collection = processing_flow.filter(list(range(10)))
    assert collection == [0, 2, 4, 6, 8], (
        f"wrong value was return from filter function, expected '[0, 2, 4, 6, 8]', found: '{collection}'"
    )
    assert failed_idx == -1, f"wrong filed index return, expected: '-1' found: {failed_idx}"


def test_evaluate_functions(processing_flow):

    record = KafkaRecord("key_c", 3, "test_topic")
    expected_result = ("key_c", 18)

    processed_results = processing_flow.evaluate_callbacks(record)

    assert processed_results == expected_result, (
        f"callbacks evaluation return with wrong results, expected: '{expected_result}', found: '{processed_results}'"
    )


def test_exception_on_evaluating_functions(processing_flow_callback_exception):
    record = KafkaRecord("key_c", 3, "test_topic")

    with pytest.raises(FailToProcessMessage):
        processing_flow_callback_exception.evaluate_callbacks(record)


def test_exception_filter_processing_flow(processing_flow_filter_exception):

    failed_idx, collection = processing_flow_filter_exception.filter(list(range(10)))

    assert failed_idx == 1, f"wrong value was returned for failed index, expected: 1, found: {failed_idx}"
    assert collection == [0], f"wrong collection was returned for collection, expected: '[0]', found: '{collection}'"


def test_filter_without_filtering_function(processing_flow_wo_filtering_function):
    failed_idx, collection = processing_flow_wo_filtering_function.filter(list(range(10)))

    assert failed_idx == -1, f"wrong filed index return, expected: '-1' found: {failed_idx}"
    assert collection == collection, (
        "since no filtering function was set no change was expected on the original collection"
    )
