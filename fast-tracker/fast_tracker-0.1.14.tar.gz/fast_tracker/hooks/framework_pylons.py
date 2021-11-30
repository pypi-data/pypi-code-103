# -*- coding: utf-8 -*-

import fast_tracker.api.transaction
import fast_tracker.api.transaction_name
import fast_tracker.api.function_trace
import fast_tracker.api.error_trace
import fast_tracker.api.object_wrapper
import fast_tracker.api.import_hook

from fast_tracker.api.time_trace import record_exception


def name_controller(self, environ, start_response):
    action = environ['pylons.routes_dict']['action']
    return "%s.%s" % (fast_tracker.api.object_wrapper.callable_name(self), action)


class capture_error(object):
    def __init__(self, wrapped):
        if isinstance(wrapped, tuple):
            (instance, wrapped) = wrapped
        else:
            instance = None
        self.__instance = instance
        self.__wrapped = wrapped

    def __get__(self, instance, klass):
        if instance is None:
            return self
        descriptor = self.__wrapped.__get__(instance, klass)
        return self.__class__((instance, descriptor))

    def __call__(self, *args, **kwargs):
        current_transaction = fast_tracker.api.transaction.current_transaction()
        if current_transaction:
            webob_exc = fast_tracker.api.import_hook.import_module('webob.exc')
            try:
                return self.__wrapped(*args, **kwargs)
            except webob_exc.HTTPException:
                raise
            except:  # Catch all
                record_exception()
                raise
        else:
            return self.__wrapped(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.__wrapped, name)


def instrument(module):
    if module.__name__ == 'pylons.wsgiapp':
        fast_tracker.api.error_trace.wrap_error_trace(module, 'PylonsApp.__call__')

    elif module.__name__ == 'pylons.controllers.core':
        fast_tracker.api.transaction_name.wrap_transaction_name(
            module, 'WSGIController.__call__', name_controller)
        fast_tracker.api.function_trace.wrap_function_trace(
            module, 'WSGIController.__call__')

        def name_WSGIController_perform_call(self, func, args):
            return fast_tracker.api.object_wrapper.callable_name(func)

        fast_tracker.api.function_trace.wrap_function_trace(
            module, 'WSGIController._perform_call',
            name_WSGIController_perform_call)
        fast_tracker.api.object_wrapper.wrap_object(
            module, 'WSGIController._perform_call', capture_error)

    elif module.__name__ == 'pylons.templating':

        fast_tracker.api.function_trace.wrap_function_trace(module, 'render_genshi')
        fast_tracker.api.function_trace.wrap_function_trace(module, 'render_mako')
        fast_tracker.api.function_trace.wrap_function_trace(module, 'render_jinja2')
