import os

import pytest
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace.status import StatusCode

from helios import initialize, HeliosBase


SERVICE_NAME = 'pytest'
ROOT_SPAN_NAME = 'test_root'

self_test = False
span_exporter = None
test_span_exporter = None
active_span = None
tracer_provider = None
tracer = None
hs_test_enabled = False


class PytestSpanAttributes:
    LIBRARY = 'testLibrary'
    NAME = 'name'
    STATUS = 'status.code'
    ERROR_MESSAGE = 'status.message'


def is_self_test(config):
    self_test_str = config.getoption('--self_test') or os.environ.get('HS_SELF_TEST', 'False')
    return self_test_str.lower() == "true"


def get_api_token(config):
    api_token = config.getoption('--hs_access_token') or os.environ.get('HS_ACCESS_TOKEN')
    if api_token is None:
        raise RuntimeError('Helios access token is missing.'
                           ' please set HS_ACCESS_TOKEN env var, '
                           ' or provide --hs_access_token argument to pytest command')
    return api_token


def is_hs_test_enabled(config):
    return config.getoption('--hs_enabled') is not None


def pytest_configure(config):
    global span_exporter, test_span_exporter, tracer_provider, tracer, self_test, hs_test_enabled

    hs_test_enabled = is_hs_test_enabled(config)
    if not hs_test_enabled:
        return

    api_token = get_api_token(config)
    collector_endpoint = config.getoption('--collector_endpoint')
    test_collector_endpoint = config.getoption('--test_collector_endpoint')
    environment = config.getoption('--environment')

    self_test = is_self_test(config)
    if self_test:
        span_exporter = InMemorySpanExporter()
        test_span_exporter = InMemorySpanExporter()

    hs = initialize(
        api_token=api_token,
        service_name=SERVICE_NAME,
        collector_endpoint=collector_endpoint,
        test_collector_endpoint=test_collector_endpoint,
        environment=environment,
        enabled=hs_test_enabled,
        span_exporter=span_exporter,
        test_span_exporter=test_span_exporter
    )

    tracer_provider = hs.get_tracer_provider()
    tracer = tracer_provider.get_tracer(__name__)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    if not hs_test_enabled:
        yield
    else:
        global active_span
        with tracer.start_as_current_span(ROOT_SPAN_NAME) as span:
            HeliosBase.set_span_as_triggered_by_helios_test(span)
            active_span = span
            # returns to test execution
            yield

        # When test is done
        active_span = None
        tracer_provider.force_flush()

        if self_test:
            run_self_test(item)


def run_self_test(item):
    expected_status = os.environ.get('HS_SELF_TEST_EXPECTED_STATUS', 'passed')
    child_span = None
    test_span = None
    child_span_name = os.environ.get('HS_SELF_TEST_EXPECTED_CHILD_SPAN')
    if span_exporter:
        for span in span_exporter.get_finished_spans():
            if span.attributes.get('otel.library.name') == child_span_name:
                child_span = span
            elif span.name == ROOT_SPAN_NAME:
                test_span = span

    assert test_span is not None
    assert test_span.attributes.get(PytestSpanAttributes.NAME) == item.location[-1]
    assert test_span.attributes.get(PytestSpanAttributes.STATUS) == (
        StatusCode.ERROR.value if expected_status != 'passed' else StatusCode.OK.value)
    if expected_status == 'passed':
        assert test_span.attributes.get(PytestSpanAttributes.ERROR_MESSAGE) == ''
    else:
        assert test_span.attributes.get(PytestSpanAttributes.ERROR_MESSAGE) != ''

    if child_span_name:
        assert child_span is not None
        assert child_span.parent.span_id == test_span.context.span_id


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # returns to test execution
    outcome = yield

    # when test is done, do nothing if hs_test not enabled
    if not hs_test_enabled:
        return

    # when test is done, extract the attributes from the test report
    result = outcome.get_result()
    if result.when == 'call':
        if active_span:
            active_span.set_attributes({
                PytestSpanAttributes.LIBRARY: 'pytest',
                PytestSpanAttributes.NAME: result.location[-1],
                PytestSpanAttributes.STATUS: (
                    StatusCode.ERROR.value if result.outcome != 'passed' else StatusCode.OK.value),
                PytestSpanAttributes.ERROR_MESSAGE: result.longreprtext,
            })


def pytest_addoption(parser):
    parser.addoption('--hs_enabled', help="enable instrumented tests", default=None)
    parser.addoption('--hs_access_token', help='access token for Helios', default=None)
    parser.addoption('--environment', help='name of the environment where the tests are running', default='')
    parser.addoption('--collector_endpoint', help='OTEL collector endpoint', default=HeliosBase.HS_DEFAULT_COLLECTOR)
    parser.addoption('--test_collector_endpoint', help='OTEL test collector endpoint',
                     default=HeliosBase.HS_DEFAULT_TEST_COLLECTOR)
    parser.addoption('--self_test', help='run tests in dry run mode', default=None)
