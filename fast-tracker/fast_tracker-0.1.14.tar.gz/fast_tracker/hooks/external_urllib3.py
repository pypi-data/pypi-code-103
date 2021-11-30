# -*- coding: utf-8 -*-

from fast_tracker.api.external_trace import ExternalTrace
from fast_tracker.common.object_wrapper import wrap_function_wrapper
from fast_tracker.common.span_enum import SpanLayerAtrr, SpanType
from fast_tracker.hooks.external_httplib2 import (
    _nr_wrapper_httplib2_endheaders_wrapper)


def _nr_wrapper_make_request_(wrapped, instance, args, kwargs):
    def _bind_params(conn, method, url, *args, **kwargs):
        return "%s://%s:%s" % (instance.scheme, conn.host, conn.port)

    url_for_apm_ui = _bind_params(*args, **kwargs)

    with ExternalTrace('urllib3', url_for_apm_ui, span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.HTTP.value):
        return wrapped(*args, **kwargs)


def instrument_urllib3_connectionpool(module):
    wrap_function_wrapper(module, 'HTTPSConnectionPool._make_request',
                          _nr_wrapper_make_request_)
    wrap_function_wrapper(module, 'HTTPConnectionPool._make_request',
                          _nr_wrapper_make_request_)


def instrument_urllib3_connection(module):
    wrap_function_wrapper(module, 'HTTPSConnection.endheaders',
                          _nr_wrapper_httplib2_endheaders_wrapper('urllib3', 'https'))

    wrap_function_wrapper(module, 'HTTPConnection.endheaders',
                          _nr_wrapper_httplib2_endheaders_wrapper('urllib3', 'http'))
