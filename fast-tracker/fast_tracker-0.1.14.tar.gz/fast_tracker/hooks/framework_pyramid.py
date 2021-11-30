# -*- coding: utf-8 -*-

from fast_tracker.api.function_trace import FunctionTrace, FunctionTraceWrapper
from fast_tracker.api.transaction import current_transaction
from fast_tracker.api.wsgi_application import wrap_wsgi_application
from fast_tracker.common.object_names import callable_name
from fast_tracker.common.object_wrapper import (FunctionWrapper, wrap_out_function,
                                                wrap_function_wrapper)
from fast_tracker.core.config import ignore_status_code


def instrument_pyramid_router(module):
    pyramid_version = None

    try:
        import pkg_resources
        pyramid_version = pkg_resources.get_distribution('pyramid').version
    except Exception:
        pass

    wrap_wsgi_application(
        module, 'Router.__call__', framework=('Pyramid', pyramid_version))


def should_ignore(exc, value, tb):
    from pyramid.httpexceptions import HTTPException
    from pyramid.exceptions import PredicateMismatch

    if isinstance(value, HTTPException):
        if ignore_status_code(value.code):
            return True

    if isinstance(value, PredicateMismatch):
        return True


def view_handler_wrapper(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if not transaction:
        return wrapped(*args, **kwargs)

    try:
        view_callable = wrapped.__original_view__ or wrapped
    except AttributeError:
        view_callable = wrapped

    name = callable_name(view_callable)

    transaction.set_transaction_name(name)

    with FunctionTrace(name) as trace:
        try:
            return wrapped(*args, **kwargs)

        except:  # Catch all
            trace.record_exception(ignore_errors=should_ignore)
            raise


def wrap_view_handler(mapped_view):
    if hasattr(mapped_view, '_nr_wrapped'):
        return mapped_view
    else:
        wrapped = FunctionWrapper(mapped_view, view_handler_wrapper)
        wrapped._nr_wrapped = True
        return wrapped


def wrap_tween_factory(wrapped, instance, args, kwargs):
    handler = wrapped(*args, **kwargs)
    return FunctionTraceWrapper(handler)


def wrap_add_tween(wrapped, instance, args, kwargs):
    def _bind_params(name, factory, *_args, **_kwargs):
        return name, factory, _args, _kwargs

    name, factory, args, kwargs = _bind_params(*args, **kwargs)
    factory = FunctionWrapper(factory, wrap_tween_factory)
    return wrapped(name, factory, *args, **kwargs)


def default_view_mapper_wrapper(wrapped, instance, args, kwargs):
    wrapper = wrapped(*args, **kwargs)

    def _args(view, *args, **kwargs):
        return view

    view = _args(*args, **kwargs)

    def _wrapper(context, request):
        transaction = current_transaction()

        if not transaction:
            return wrapper(context, request)

        name = callable_name(view)

        with FunctionTrace(name=name) as tracer:
            try:
                return wrapper(context, request)
            finally:
                attr = instance.attr
                if attr:
                    inst = getattr(request, '__view__', None)
                    if inst is not None:
                        name = callable_name(getattr(inst, attr))
                        transaction.set_transaction_name(name, priority=1)
                        tracer.name = name
                else:
                    inst = getattr(request, '__view__', None)
                    if inst is not None:
                        method = getattr(inst, '__call__')
                        if method:
                            name = callable_name(method)
                            transaction.set_transaction_name(name, priority=1)
                            tracer.name = name

    return _wrapper


def instrument_pyramid_config_views(module):

    if hasattr(module, 'ViewDeriver'):
        wrap_out_function(module, 'ViewDeriver.__call__', wrap_view_handler)
    elif hasattr(module, 'Configurator'):
        wrap_out_function(module, 'Configurator._derive_view',
                          wrap_view_handler)

    if hasattr(module, 'DefaultViewMapper'):
        module.DefaultViewMapper.map_class_requestonly = FunctionWrapper(
            module.DefaultViewMapper.map_class_requestonly,
            default_view_mapper_wrapper)
        module.DefaultViewMapper.map_class_native = FunctionWrapper(
            module.DefaultViewMapper.map_class_native,
            default_view_mapper_wrapper)


def instrument_pyramid_config_tweens(module):
    wrap_function_wrapper(module, 'Tweens.add_explicit', wrap_add_tween)

    wrap_function_wrapper(module, 'Tweens.add_implicit', wrap_add_tween)
