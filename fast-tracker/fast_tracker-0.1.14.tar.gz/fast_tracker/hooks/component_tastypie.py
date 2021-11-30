# -*- coding: utf-8 -*-

import sys

from fast_tracker.api.function_trace import FunctionTrace
from fast_tracker.api.object_wrapper import ObjectWrapper, callable_name
from fast_tracker.api.transaction import current_transaction
from fast_tracker.api.time_trace import record_exception
from fast_tracker.common.object_wrapper import wrap_function_wrapper
from fast_tracker.core.config import ignore_status_code


def _nr_wrap_handle_exception(wrapped, instance, args, kwargs):
    response = wrapped(*args, **kwargs)

    if not ignore_status_code(response.status_code):
        record_exception()

    return response


def outer_fn_wrapper(outer_fn, instance, args, kwargs):
    view_name = args[0]

    meta = getattr(instance, "_meta", None)

    if meta is None:
        group = 'Python/TastyPie/Api'
        name = instance.api_name
        callback = getattr(instance, 'top_level', None)
    elif meta.api_name is not None:
        group = 'Python/TastyPie/Api'
        name = '%s/%s/%s' % (meta.api_name, meta.resource_name, view_name)
        callback = getattr(instance, view_name, None)
    else:
        group = 'Python/TastyPie/Resource'
        name = '%s/%s' % (meta.resource_name, view_name)
        callback = getattr(instance, view_name, None)

    if callback is not None:
        name = callable_name(callback)
        group = None

    def inner_fn_wrapper(inner_fn, instance, args, kwargs):
        transaction = current_transaction()

        if transaction is None or name is None:
            return inner_fn(*args, **kwargs)

        transaction.set_transaction_name(name, group, priority=5)

        with FunctionTrace(name, group):
            return inner_fn(*args, **kwargs)

    result = outer_fn(*args, **kwargs)

    return ObjectWrapper(result, None, inner_fn_wrapper)


def instrument_tastypie_resources(module):
    _wrap_view = module.Resource.wrap_view
    module.Resource.wrap_view = ObjectWrapper(
        _wrap_view, None, outer_fn_wrapper)

    wrap_function_wrapper(module, 'Resource._handle_500',
                          _nr_wrap_handle_exception)


def instrument_tastypie_api(module):
    _wrap_view = module.Api.wrap_view
    module.Api.wrap_view = ObjectWrapper(_wrap_view, None, outer_fn_wrapper)
