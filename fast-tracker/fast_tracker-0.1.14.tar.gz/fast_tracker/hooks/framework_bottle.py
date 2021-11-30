# -*- coding: utf-8 -*-

import functools

from fast_tracker.api.function_trace import (FunctionTrace, FunctionTraceWrapper,
                                             wrap_function_trace)
from fast_tracker.api.transaction import current_transaction
from fast_tracker.api.wsgi_application import wrap_wsgi_application
from fast_tracker.common.object_names import callable_name
from fast_tracker.common.object_wrapper import (wrap_out_function,
                                                function_wrapper, ObjectProxy, wrap_object_attribute,
                                                wrap_function_wrapper)
from fast_tracker.core.config import ignore_status_code

module_bottle = None


def should_ignore(exc, value, tb):
    if isinstance(value, module_bottle.HTTPResponse):
        if hasattr(value, 'status_code'):
            if ignore_status_code(value.status_code):
                return True
        elif hasattr(value, 'status'):
            if ignore_status_code(value.status):
                return True
        elif hasattr(value, 'http_status_code'):
            if ignore_status_code(value.http_status_code):
                return True

    elif hasattr(module_bottle, 'RouteReset'):
        if isinstance(value, module_bottle.RouteReset):
            return True


@function_wrapper
def callback_wrapper(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    name = callable_name(wrapped)

    transaction.set_transaction_name(name, priority=2)

    with FunctionTrace(name) as trace:
        try:
            return wrapped(*args, **kwargs)

        except:  # Catch all
            trace.record_exception(ignore_errors=should_ignore)
            raise


def output_wrapper_Bottle_match(result):
    callback, args = result
    return callback_wrapper(callback), args


def output_wrapper_Route_make_callback(callback):
    return callback_wrapper(callback)


class proxy_Bottle_error_handler(ObjectProxy):

    def get(self, status, default=None):
        transaction = current_transaction()

        if transaction is None:
            return self.__wrapped__.get(status, default)

        handler = self.__wrapped__.get(status)

        if handler:
            name = callable_name(handler)
            transaction.set_transaction_name(name, priority=1)
            handler = FunctionTraceWrapper(handler, name=name)
        else:
            transaction.set_transaction_name(str(status),
                                             group='StatusCode', priority=1)

        return handler or default


def wrapper_auth_basic(wrapped, instance, args, kwargs):

    decorator = wrapped(*args, **kwargs)

    def _decorator(func):
        return functools.wraps(func)(decorator(func))

    return _decorator


def instrument_bottle(module):
    global module_bottle
    module_bottle = module

    framework_details = ('Bottle', getattr(module, '__version__'))

    if hasattr(module.Bottle, 'wsgi'):  # version >= 0.9
        wrap_wsgi_application(module, 'Bottle.wsgi',
                              framework=framework_details)
    elif hasattr(module.Bottle, '__call__'):  # version < 0.9
        wrap_wsgi_application(module, 'Bottle.__call__',
                              framework=framework_details)

    if (hasattr(module, 'Route') and
            hasattr(module.Route, '_make_callback')):  # version >= 0.10
        wrap_out_function(module, 'Route._make_callback',
                          output_wrapper_Route_make_callback)
    elif hasattr(module.Bottle, '_match'):  # version >= 0.9
        wrap_out_function(module, 'Bottle._match',
                          output_wrapper_Bottle_match)
    elif hasattr(module.Bottle, 'match_url'):  # version < 0.9
        wrap_out_function(module, 'Bottle.match_url',
                          output_wrapper_Bottle_match)

    wrap_object_attribute(module, 'Bottle.error_handler',
                          proxy_Bottle_error_handler)

    if hasattr(module, 'auth_basic'):
        wrap_function_wrapper(module, 'auth_basic', wrapper_auth_basic)

    if hasattr(module, 'SimpleTemplate'):
        wrap_function_trace(module, 'SimpleTemplate.render')

    if hasattr(module, 'MakoTemplate'):
        wrap_function_trace(module, 'MakoTemplate.render')

    if hasattr(module, 'CheetahTemplate'):
        wrap_function_trace(module, 'CheetahTemplate.render')

    if hasattr(module, 'Jinja2Template'):
        wrap_function_trace(module, 'Jinja2Template.render')

    if hasattr(module, 'SimpleTALTemplate'):
        wrap_function_trace(module, 'SimpleTALTemplate.render')
