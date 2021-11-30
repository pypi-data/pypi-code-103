# -*- coding: utf-8 -*-

import functools
import textwrap
import inspect
import sys
from fast_tracker.api.function_trace import function_trace
from fast_tracker.api.transaction import current_transaction
from fast_tracker.core.config import ignore_status_code
from fast_tracker.api.external_trace import ExternalTrace
from fast_tracker.api.time_trace import record_exception
from fast_tracker.api.web_transaction import WebTransaction
from fast_tracker.api.application import application_instance
from fast_tracker.common.object_wrapper import (
    function_wrapper, wrap_function_wrapper)
from fast_tracker.common.span_enum import SpanLayerAtrr, SpanType
from fast_tracker.common.async_proxy import async_proxy
from fast_tracker.common.object_names import callable_name

_VERSION = None
_instrumented = set()


def _store_version_info():
    import tornado
    global _VERSION

    try:
        _VERSION = '.'.join(map(str, tornado.version_info))
    except:
        pass

    return tornado.version_info


def convert_yielded(*args, **kwargs):
    global convert_yielded
    from tornado.gen import convert_yielded as _convert_yielded
    convert_yielded = _convert_yielded
    return _convert_yielded(*args, **kwargs)


def _wrap_if_not_wrapped(obj, attr, wrapper):
    wrapped = getattr(obj, attr, None)

    if not callable(wrapped):
        return

    if not (hasattr(wrapped, '__wrapped__') and
            wrapped.__wrapped__ in _instrumented):
        setattr(obj, attr, wrapper(wrapped))
        _instrumented.add(wrapped)


def _bind_start_request(server_conn, request_conn, *args, **kwargs):
    return request_conn


def _bind_headers_received(start_line, headers, *args, **kwargs):
    return start_line, headers


def wrap_headers_received(request_conn):
    @function_wrapper
    def _wrap_headers_received(wrapped, instance, args, kwargs):
        start_line, headers = _bind_headers_received(*args, **kwargs)
        port = None

        try:
            sockname = request_conn.stream.socket.getsockname()
            if isinstance(sockname, tuple):
                port = sockname[1]
        except:
            pass

        path, sep, query = start_line.path.partition('?')

        transaction = WebTransaction(
            application=application_instance(),
            name=callable_name(instance),
            port=port,
            request_method=start_line.method,
            request_path=path,
            query_string=query,
            headers=headers,
        )
        transaction.__enter__()

        if not transaction.enabled:
            return wrapped(*args, **kwargs)

        transaction.add_framework_info('Tornado', _VERSION)

        request_conn._nr_transaction = transaction

        vars(instance).pop('headers_received')

        return wrapped(*args, **kwargs)

    return _wrap_headers_received


def _bind_response_headers(start_line, headers, *args, **kwargs):
    return start_line.code, headers


@function_wrapper
def wrap_write_headers(wrapped, instance, args, kwargs):
    transaction = getattr(instance, '_nr_transaction', None)

    if transaction:
        http_status, headers = _bind_response_headers(*args, **kwargs)
        cat_headers = transaction.process_response(http_status, headers)

        for name, value in cat_headers:
            headers.add(name, value)

    return wrapped(*args, **kwargs)


@function_wrapper
def wrap_finish(wrapped, instance, args, kwargs):
    try:
        return wrapped(*args, **kwargs)
    finally:
        transaction = getattr(instance, '_nr_transaction', None)
        if transaction:
            record_exception(
                *sys.exc_info(),
                ignore_errors=should_ignore)
            transaction.__exit__(None, None, None)
            instance._nr_transaction = None


def wrap_start_request(wrapped, instance, args, kwargs):
    request_conn = _bind_start_request(*args, **kwargs)
    message_delegate = wrapped(*args, **kwargs)

    wrapper = wrap_headers_received(request_conn)
    message_delegate.headers_received = wrapper(
        message_delegate.headers_received)

    _wrap_if_not_wrapped(
        type(request_conn), 'write_headers', wrap_write_headers)

    _wrap_if_not_wrapped(
        type(request_conn), 'finish', wrap_finish)

    return message_delegate


def instrument_tornado_httpserver(module):
    version_info = _store_version_info()

    # Do not instrument Tornado versions < 6.0
    if version_info[0] < 6:
        return

    wrap_function_wrapper(
        module, 'HTTPServer.start_request', wrap_start_request)


def should_ignore(exc, value, tb):
    from tornado.web import HTTPError

    if exc is HTTPError:
        status_code = value.status_code
        if ignore_status_code(status_code):
            return True


def _nr_wrapper__NormalizedHeaderCache___missing__(
        wrapped, instance, args, kwargs):
    def _bind_params(key, *args, **kwargs):
        return key

    key = _bind_params(*args, **kwargs)

    normalized = wrapped(*args, **kwargs)

    if key.startswith('X-fast_tracker'):
        instance[key] = key
        return key

    return normalized


def _nr_wrapper_normalize_header(wrapped, instance, args, kwargs):
    def _bind_params(name, *args, **kwargs):
        return name

    name = _bind_params(*args, **kwargs)
    if name.startswith('X-fast_tracker'):
        return name

    return wrapped(*args, **kwargs)


def instrument_tornado_httputil(module):
    version_info = _store_version_info()

    # Do not instrument Tornado versions < 6.0
    if version_info[0] < 6:
        return

    if hasattr(module, '_NormalizedHeaderCache'):
        wrap_function_wrapper(module, '_NormalizedHeaderCache.__missing__',
                              _nr_wrapper__NormalizedHeaderCache___missing__)
    elif hasattr(module, '_normalize_header'):
        wrap_function_wrapper(module, '_normalize_header',
                              _nr_wrapper_normalize_header)


def _prepare_request(request, raise_error=True, **kwargs):
    from tornado.httpclient import HTTPRequest

    # request is either a string or a HTTPRequest object
    if not isinstance(request, HTTPRequest):
        request = HTTPRequest(request, **kwargs)

    return request, raise_error


def create_client_wrapper(wrapped, trace):
    values = {'wrapper': None, 'wrapped': wrapped,
              'trace': trace, 'functools': functools}
    wrapper = textwrap.dedent("""
    @functools.wraps(wrapped)
    async def wrapper(req, raise_error):
        with trace:
            response = None
            try:
                response = await wrapped(req, raise_error=raise_error)
            except Exception as e:
                response = getattr(e, 'response', None)
                raise
            finally:
                if response:
                    trace.process_response_headers(response.headers.get_all())
            return response
    """)
    exec(wrapper, values)
    return values['wrapper']


def wrap_httpclient_fetch(wrapped, instance, args, kwargs):
    try:
        req, raise_error = _prepare_request(*args, **kwargs)
    except:
        return wrapped(*args, **kwargs)

    trace = ExternalTrace(
        'tornado', req.url, req.method.upper(), span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.HTTP.value)

    outgoing_headers = trace.generate_request_headers(current_transaction())
    for header_name, header_value in outgoing_headers:
        # User headers should override our CAT headers
        if header_name in req.headers:
            continue
        req.headers[header_name] = header_value

    try:
        fetch = create_client_wrapper(wrapped, trace)
    except:
        return wrapped(*args, **kwargs)

    return convert_yielded(fetch(req, raise_error))


def instrument_tornado_httpclient(module):
    version_info = _store_version_info()

    # Do not instrument Tornado versions < 6.0
    if version_info[0] < 6:
        return

    wrap_function_wrapper(module,
                          'AsyncHTTPClient.fetch', wrap_httpclient_fetch)


def _nr_rulerouter_process_rule(wrapped, instance, args, kwargs):
    def _bind_params(rule, *args, **kwargs):
        return rule

    rule = _bind_params(*args, **kwargs)

    _wrap_handlers(rule)

    return wrapped(*args, **kwargs)


@function_wrapper
def _nr_method(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    if getattr(transaction, '_method_seen', None):
        return wrapped(*args, **kwargs)

    name = callable_name(wrapped)
    transaction.set_transaction_name(name, priority=2)
    transaction._method_seen = True
    if getattr(wrapped, '__tornado_coroutine__', False):
        return wrapped(*args, **kwargs)
    return function_trace(name=name)(wrapped)(*args, **kwargs)


def _wrap_handlers(rule):
    if isinstance(rule, (tuple, list)):
        handler = rule[1]
    elif hasattr(rule, 'target'):
        handler = rule.target
    elif hasattr(rule, 'handler_class'):
        handler = rule.handler_class
    else:
        return

    from tornado.web import RequestHandler
    from tornado.websocket import WebSocketHandler

    if isinstance(handler, (tuple, list)):
        for subrule in handler:
            _wrap_handlers(subrule)
        return

    elif (not inspect.isclass(handler) or
          issubclass(handler, WebSocketHandler) or
          not issubclass(handler, RequestHandler)):

        return

    if not hasattr(handler, 'SUPPORTED_METHODS'):
        return

    for request_method in handler.SUPPORTED_METHODS:
        _wrap_if_not_wrapped(handler, request_method.lower(), _nr_method)


def _nr_wrapper_web_requesthandler_init(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    name = callable_name(instance)
    transaction.set_transaction_name(name, priority=1)
    return wrapped(*args, **kwargs)


def instrument_tornado_routing(module):
    version_info = _store_version_info()

    if version_info[0] < 6:
        return

    wrap_function_wrapper(module, 'RuleRouter.process_rule',
                          _nr_rulerouter_process_rule)


def instrument_tornado_web(module):
    version_info = _store_version_info()

    if version_info[0] < 6:
        return

    wrap_function_wrapper(module, 'RequestHandler.__init__',
                          _nr_wrapper_web_requesthandler_init)
    wrap_function_wrapper(module, 'RequestHandler._execute',
                          track_loop_time)


class TornadoContext(object):
    def __init__(self):
        self.transaction = None

    def __enter__(self):
        transaction = self.transaction
        if not transaction:
            transaction = self.transaction = current_transaction()

    def __exit__(self, exc, value, tb):
        pass
            

def track_loop_time(wrapped, instance, args, kwargs):
    proxy = async_proxy(wrapped)
    if proxy:
        return proxy(wrapped(*args, **kwargs), TornadoContext())

    return wrapped(*args, **kwargs)
