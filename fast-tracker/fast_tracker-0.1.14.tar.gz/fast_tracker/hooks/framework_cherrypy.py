# -*- coding: utf-8 -*-

from fast_tracker.api.function_trace import FunctionTrace, wrap_function_trace
from fast_tracker.api.transaction import current_transaction
from fast_tracker.api.time_trace import record_exception
from fast_tracker.api.wsgi_application import wrap_wsgi_application
from fast_tracker.common.object_names import callable_name
from fast_tracker.common.object_wrapper import (ObjectProxy, function_wrapper,
                                                wrap_function_wrapper)
from fast_tracker.core.config import ignore_status_code
from fast_tracker.api.error_trace import wrap_error_trace


def framework_details():
    import cherrypy
    return ('CherryPy', getattr(cherrypy, '__version__', None))


def should_ignore(exc, value, tb):
    from cherrypy import HTTPError, HTTPRedirect

    if isinstance(value, (HTTPError, HTTPRedirect)):
        code = getattr(value, 'code', value.status)

        if ignore_status_code(code):
            return True
    module = value.__class__.__module__
    name = value.__class__.__name__
    fullname = '%s:%s' % (module, name)

    ignore_exceptions = ('cherrypy._cperror:InternalRedirect',)

    if fullname in ignore_exceptions:
        return True


@function_wrapper
def handler_wrapper(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    name = callable_name(wrapped)
    transaction.set_transaction_name(name=name)
    with FunctionTrace(name=name):
        return wrapped(*args, **kwargs)


class ResourceProxy(ObjectProxy):

    def __getattr__(self, name):
        attr = super(ResourceProxy, self).__getattr__(name)
        return name.isupper() and handler_wrapper(attr) or attr


def wrapper_Dispatcher_find_handler(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    try:
        obj, vpath = wrapped(*args, **kwargs)

    except:  # Catch all
        record_exception()
        raise

    if obj:
        if instance.__class__.__name__ == 'MethodDispatcher':
            transaction.set_transaction_name('405', group='StatusCode')
            obj = ResourceProxy(obj)

        else:
            obj = handler_wrapper(obj)

    else:
        transaction.set_transaction_name('404', group='StatusCode')

    return obj, vpath


def wrapper_RoutesDispatcher_find_handler(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    try:
        handler = wrapped(*args, **kwargs)

    except:  # Catch all
        record_exception()
        raise

    if handler:
        handler = handler_wrapper(handler)

    else:

        transaction.set_transaction_name('404', group='StatusCode')

    return handler


def instrument_cherrypy__cpreqbody(module):
    wrap_function_trace(module, 'process_multipart')
    wrap_function_trace(module, 'process_multipart_form_data')


def instrument_cherrypy__cprequest(module):
    wrap_function_trace(module, 'Request.handle_error')


def instrument_cherrypy__cpdispatch(module):
    wrap_function_wrapper(module, 'Dispatcher.find_handler',
                          wrapper_Dispatcher_find_handler)
    wrap_function_wrapper(module, 'RoutesDispatcher.find_handler',
                          wrapper_RoutesDispatcher_find_handler)
    wrap_error_trace(module, 'PageHandler.__call__',
                     ignore_errors=should_ignore)


def instrument_cherrypy__cpwsgi(module):
    wrap_wsgi_application(module, 'CPWSGIApp.__call__',
                          framework=framework_details())


def instrument_cherrypy__cptree(module):
    wrap_wsgi_application(module, 'Application.__call__',
                          framework=framework_details())
