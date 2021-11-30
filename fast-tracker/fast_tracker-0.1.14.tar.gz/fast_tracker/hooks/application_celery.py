# -*- coding: utf-8 -*-

import functools

from fast_tracker.api.application import application_instance
from fast_tracker.api.background_task import BackgroundTask
from fast_tracker.api.function_trace import FunctionTrace
from fast_tracker.api.pre_function import wrap_pre_function
from fast_tracker.api.object_wrapper import callable_name, ObjectWrapper
from fast_tracker.api.transaction import current_transaction
from fast_tracker.core.agent import shutdown_agent


def CeleryTaskWrapper(wrapped, application=None, name=None):
    def wrapper(wrapped, instance, args, kwargs):
        transaction = current_transaction(active_only=False)

        if callable(name):
            if instance is not None:
                _name = name(instance, *args, **kwargs)
            else:
                _name = name(*args, **kwargs)

        elif name is None:
            _name = callable_name(wrapped)

        else:
            _name = name

        def _application():
            if hasattr(application, 'activate'):
                return application
            return application_instance(application)

        if transaction and (transaction.ignore_transaction or
                            transaction.stopped):
            return wrapped(*args, **kwargs)

        elif transaction:
            with FunctionTrace(callable_name(wrapped)):
                return wrapped(*args, **kwargs)

        else:
            with BackgroundTask(_application(), _name, 'Celery'):
                return wrapped(*args, **kwargs)

    class _ObjectWrapper(ObjectWrapper):
        def run(self, *args, **kwargs):
            return self.__call__(*args, **kwargs)

    obj = _ObjectWrapper(wrapped, None, wrapper)

    return obj


def instrument_celery_app_task(module):
    if hasattr(module, 'BaseTask'):

        def task_name(task, *args, **kwargs):
            return task.name

        if module.BaseTask.__module__ == module.__name__:
            module.BaseTask.__call__ = CeleryTaskWrapper(
                module.BaseTask.__call__, name=task_name)


def instrument_celery_execute_trace(module):
    if hasattr(module, 'build_tracer'):
        _build_tracer = module.build_tracer

        def build_tracer(name, task, *args, **kwargs):
            task = task or module.tasks[name]
            task = CeleryTaskWrapper(task, name=name)
            return _build_tracer(name, task, *args, **kwargs)

        module.build_tracer = build_tracer


def instrument_celery_worker(module):
    if hasattr(module, 'process_initializer'):
        _process_initializer = module.process_initializer

        @functools.wraps(module.process_initializer)
        def process_initializer(*args, **kwargs):
            application_instance().activate()
            return _process_initializer(*args, **kwargs)

        module.process_initializer = process_initializer


def instrument_celery_loaders_base(module):
    def force_application_activation(*args, **kwargs):
        application_instance().activate()

    wrap_pre_function(module, 'BaseLoader.init_worker',
                      force_application_activation)


def instrument_billiard_pool(module):
    def force_agent_shutdown(*args, **kwargs):
        shutdown_agent()

    if hasattr(module, 'Worker'):
        wrap_pre_function(module, 'Worker._do_exit', force_agent_shutdown)
