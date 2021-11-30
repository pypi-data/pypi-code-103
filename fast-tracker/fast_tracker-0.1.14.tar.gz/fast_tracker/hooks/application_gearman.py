# -*- coding: utf-8 -*-
from fast_tracker.api.application import application_instance as default_application
from fast_tracker.common.object_wrapper import (wrap_function_wrapper,
                                                FunctionWrapper)
from fast_tracker.api.background_task import BackgroundTask
from fast_tracker.api.function_trace import FunctionTrace, wrap_function_trace
from fast_tracker.api.transaction import current_transaction
from fast_tracker.api.time_trace import current_trace
from fast_tracker.common.object_names import callable_name
from fast_tracker.common.span_enum import SpanLayerAtrr, SpanType
from fast_tracker.api.external_trace import ExternalTrace


def instrument_gearman_client(module):
    wrap_function_trace(module, 'GearmanClient.submit_job')
    wrap_function_trace(module, 'GearmanClient.submit_multiple_jobs')
    wrap_function_trace(module, 'GearmanClient.submit_multiple_requests')
    wrap_function_trace(module, 'GearmanClient.wait_until_jobs_accepted')
    wrap_function_trace(module, 'GearmanClient.wait_until_jobs_completed')
    wrap_function_trace(module, 'GearmanClient.get_job_status')
    wrap_function_trace(module, 'GearmanClient.get_job_statuses')
    wrap_function_trace(module, 'GearmanClient.wait_until_job_statuses_received')


def wrapper_GearmanConnectionManager_poll_connections_until_stopped(
        wrapped, instance, args, kwargs):
    def _bind_params(submitted_connections, *args, **kwargs):
        return submitted_connections

    submitted_connections = _bind_params(*args, **kwargs)

    if not submitted_connections:
        return wrapped(*args, **kwargs)

    first_connection = list(submitted_connections)[0]

    url = 'gearman://%s:%s' % (first_connection.gearman_host,
                               first_connection.gearman_port)

    with ExternalTrace('gearman', url, span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.HTTP.value):
        return wrapped(*args, **kwargs)


def wrapper_GearmanConnectionManager_handle_function(wrapped, instance,
                                                     args, kwargs):
    def _bind_params(current_connection, *args, **kwargs):
        return current_connection

    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    tracer = current_trace()

    if not isinstance(tracer, ExternalTrace):
        return wrapped(*args, **kwargs)

    if not tracer.url.startswith('gearman:'):
        return wrapped(*args, **kwargs)

    current_connection = _bind_params(*args, **kwargs)

    tracer.url = 'gearman://%s:%s' % (current_connection.gearman_host,
                                      current_connection.gearman_port)

    return wrapped(*args, **kwargs)


def instrument_gearman_connection_manager(module):
    wrap_function_wrapper(module, 'GearmanConnectionManager.handle_read',
                          wrapper_GearmanConnectionManager_handle_function)
    wrap_function_wrapper(module, 'GearmanConnectionManager.handle_write',
                          wrapper_GearmanConnectionManager_handle_function)
    wrap_function_wrapper(module, 'GearmanConnectionManager.handle_error',
                          wrapper_GearmanConnectionManager_handle_function)

    wrap_function_wrapper(module,
                          'GearmanConnectionManager.poll_connections_until_stopped',
                          wrapper_GearmanConnectionManager_poll_connections_until_stopped)


def wrapper_GearmanWorker_on_job_execute(wrapped, instance, args, kwargs):
    def _bind_params(current_job, *args, **kwargs):
        return current_job

    application = default_application()
    current_job = _bind_params(*args, **kwargs)

    with BackgroundTask(application, current_job.task, 'Gearman'):
        return wrapped(*args, **kwargs)


def wrapper_callback_function(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    with FunctionTrace(callable_name(wrapped)) as trace:
        try:
            return wrapped(*args, **kwargs)
        except:  # Catch all
            trace.record_exception()
            raise


def wrapper_GearmanWorker_register_task(wrapped, instance, args, kwargs):
    def _bind_params(task, callback_function, *args, **kwargs):
        return task, callback_function, args, kwargs

    task, callback_function, _args, _kwargs = _bind_params(*args, **kwargs)
    callback_function = FunctionWrapper(callback_function,
                                        wrapper_callback_function)

    return wrapped(task, callback_function, *_args, **_kwargs)


def instrument_gearman_worker(module):
    wrap_function_wrapper(module, 'GearmanWorker.on_job_execute',
                          wrapper_GearmanWorker_on_job_execute)
    wrap_function_wrapper(module, 'GearmanWorker.register_task',
                          wrapper_GearmanWorker_register_task)
