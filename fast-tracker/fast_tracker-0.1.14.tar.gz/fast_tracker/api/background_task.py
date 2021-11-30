# -*- coding: utf-8 -*-


import functools
import sys

from fast_tracker.api.application import Application, application_instance
from fast_tracker.api.transaction import Transaction, current_transaction
from fast_tracker.common.async_proxy import async_proxy, TransactionContext
from fast_tracker.common.object_names import callable_name
from fast_tracker.common.object_wrapper import FunctionWrapper, wrap_object


class BackgroundTask(Transaction):

    def __init__(self, application, name, group=None):
        super(BackgroundTask, self).__init__(application)
        self.background_task = True
        self._ref_count = 0
        self._is_finalized = False
        self._request_handler_finalize = False
        self._server_adapter_finalize = False
        if not self.enabled:
            return
        self.set_transaction_name(name, group, priority=1)


def BackgroundTaskWrapper(wrapped, application=None, name=None, group=None):

    def wrapper(wrapped, instance, args, kwargs):
        if callable(name):
            if instance is not None:
                _name = name(instance, *args, **kwargs)
            else:
                _name = name(*args, **kwargs)

        elif name is None:
            _name = callable_name(wrapped)

        else:
            _name = name

        if callable(group):
            if instance is not None:
                _group = group(instance, *args, **kwargs)
            else:
                _group = group(*args, **kwargs)

        else:
            _group = group

        transaction = current_transaction(active_only=False)

        if transaction:
            if transaction.ignore_transaction or transaction.stopped:
                return wrapped(*args, **kwargs)

            if not transaction.background_task:
                transaction.background_task = True
                transaction.set_transaction_name(_name, _group)
            return wrapped(*args, **kwargs)

        if type(application) != Application:
            _application = application_instance(application)
        else:
            _application = application

        manager = BackgroundTask(_application, _name, _group)

        proxy = async_proxy(wrapped)
        if proxy:
            context_manager = TransactionContext(manager)
            return proxy(wrapped(*args, **kwargs), context_manager)

        success = True

        try:
            manager.__enter__()
            try:
                return wrapped(*args, **kwargs)
            except:
                success = False
                if not manager.__exit__(*sys.exc_info()):
                    raise
        finally:
            if success and manager._ref_count == 0:
                manager._is_finalized = True
                manager.__exit__(None, None, None)
            else:
                manager._request_handler_finalize = True
                manager._server_adapter_finalize = True

                old_transaction = current_transaction()
                if old_transaction is not None:
                    old_transaction.drop_transaction()

    return FunctionWrapper(wrapped, wrapper)


def background_task(application=None, name=None, group=None):
    return functools.partial(BackgroundTaskWrapper, application=application, name=name, group=group)


def wrap_background_task(module, object_path, application=None, name=None, group=None):
    wrap_object(module, object_path, BackgroundTaskWrapper, (application, name, group))
