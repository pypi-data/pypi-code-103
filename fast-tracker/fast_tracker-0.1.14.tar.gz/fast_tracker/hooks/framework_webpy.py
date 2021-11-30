# -*- coding: utf-8 -*-

import fast_tracker.packages.six as six

import fast_tracker.api.transaction
import fast_tracker.api.function_trace
import fast_tracker.api.in_function
import fast_tracker.api.out_function
import fast_tracker.api.pre_function
from fast_tracker.api.object_wrapper import callable_name
from fast_tracker.api.wsgi_application import WSGIApplicationWrapper
from fast_tracker.api.time_trace import record_exception


def transaction_name_delegate(*args, **kwargs):
    transaction = fast_tracker.api.transaction.current_transaction()
    if transaction:
        if isinstance(args[1], six.string_types):
            f = args[1]
        else:
            f = callable_name(args[1])
        transaction.set_transaction_name(f)
    return args, kwargs


def wrap_handle_exception(self):
    transaction = fast_tracker.api.transaction.current_transaction()
    if transaction:
        record_exception()


def template_name(render_obj, name):
    return name


def instrument(module):
    if module.__name__ == 'web.application':
        fast_tracker.api.out_function.wrap_out_function(
            module, 'application.wsgifunc', WSGIApplicationWrapper)
        fast_tracker.api.in_function.wrap_in_function(
            module, 'application._delegate', transaction_name_delegate)
        fast_tracker.api.pre_function.wrap_pre_function(
            module, 'application.internalerror', wrap_handle_exception)

    elif module.__name__ == 'web.template':
        fast_tracker.api.function_trace.wrap_function_trace(
            module, 'render.__getattr__', template_name, 'Template/Render')
