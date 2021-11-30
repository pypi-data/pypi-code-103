# -*- coding: utf-8 -*-

import logging
import sys
import weakref
import UserList

import fast_tracker.api.application
import fast_tracker.api.object_wrapper
import fast_tracker.api.transaction
import fast_tracker.api.web_transaction
import fast_tracker.api.function_trace
import fast_tracker.api.error_trace

from fast_tracker.api.time_trace import record_exception

_logger = logging.getLogger(__name__)


class RequestProcessWrapper(object):

    def __init__(self, wrapped):
        if isinstance(wrapped, tuple):
            (instance, wrapped) = wrapped
        else:
            instance = None

        fast_tracker.api.object_wrapper.update_wrapper(self, wrapped)

        self._nr_instance = instance
        self._nr_next_object = wrapped

        if not hasattr(self, '_nr_last_object'):
            self._nr_last_object = wrapped

    def __get__(self, instance, klass):
        if instance is None:
            return self
        descriptor = self._nr_next_object.__get__(instance, klass)
        return self.__class__((instance, descriptor))

    def __call__(self):
        assert self._nr_instance != None

        transaction = fast_tracker.api.transaction.current_transaction()

        if transaction:
            return self._nr_next_object()

        application = fast_tracker.api.application.application_instance()
        environ = {}

        environ['REQUEST_URI'] = self._nr_instance.path

        transaction = fast_tracker.api.web_transaction.WSGIWebTransaction(
            application, environ)

        if not transaction.enabled:
            return self._nr_next_object()

        transaction.__enter__()

        self._nr_instance._nr_transaction = transaction

        self._nr_instance._nr_is_deferred_callback = False
        self._nr_instance._nr_is_request_finished = False
        self._nr_instance._nr_wait_function_trace = None

        transaction._nr_current_request = weakref.ref(self._nr_instance)

        try:

            with fast_tracker.api.function_trace.FunctionTrace(
                    name='Request/Process', group='Python/Twisted'):
                result = self._nr_next_object()

            if self._nr_instance._nr_is_request_finished:
                transaction.__exit__(None, None, None)
                self._nr_instance._nr_transaction = None
                self._nr_instance = None

            else:
                self._nr_instance._nr_wait_function_trace = \
                    fast_tracker.api.function_trace.FunctionTrace(
                        name='Deferred/Wait',
                        group='Python/Twisted')

                self._nr_instance._nr_wait_function_trace.__enter__()
                transaction.drop_transaction()

        except:  # Catch all

            _logger.exception('Unexpected exception raised by Twisted.Web '
                              'Request.process() exception.')

            transaction.__exit__(*sys.exc_info())
            self._nr_instance._nr_transaction = None
            self._nr_instance = None

            raise

        return result


class RequestFinishWrapper(object):

    def __init__(self, wrapped):
        if isinstance(wrapped, tuple):
            (instance, wrapped) = wrapped
        else:
            instance = None

        fast_tracker.api.object_wrapper.update_wrapper(self, wrapped)

        self._nr_instance = instance
        self._nr_next_object = wrapped

        if not hasattr(self, '_nr_last_object'):
            self._nr_last_object = wrapped

    def __get__(self, instance, klass):
        if instance is None:
            return self
        descriptor = self._nr_next_object.__get__(instance, klass)
        return self.__class__((instance, descriptor))

    def __call__(self):
        assert self._nr_instance != None

        if not hasattr(self._nr_instance, '_nr_transaction'):
            return self._nr_next_object()

        transaction = self._nr_instance._nr_transaction

        if self._nr_instance._nr_wait_function_trace:
            if fast_tracker.api.transaction.current_transaction():
                _logger.debug('The Twisted.Web request finish() method is '
                              'being called while in wait state but there is '
                              'already a current transaction.')
            else:
                transaction.save_transaction()

        elif not fast_tracker.api.transaction.current_transaction():
            _logger.debug('The Twisted.Web request finish() method is '
                          'being called from request process() method or a '
                          'deferred but there is not a current transaction.')

        self._nr_instance._nr_is_request_finished = True

        if self._nr_instance._nr_is_deferred_callback:

            try:
                with fast_tracker.api.function_trace.FunctionTrace(
                        name='Request/Finish', group='Python/Twisted'):
                    result = self._nr_next_object()

            except:  # Catch all
                record_exception(*sys.exc_info())
                raise

        elif self._nr_instance._nr_wait_function_trace:

            try:
                self._nr_instance._nr_wait_function_trace.__exit__(
                    None, None, None)

                with fast_tracker.api.function_trace.FunctionTrace(
                        name='Request/Finish', group='Python/Twisted'):
                    result = self._nr_next_object()

                transaction.__exit__(None, None, None)

            except:  # Catch all
                transaction.__exit__(*sys.exc_info())
                raise

            finally:
                self._nr_instance._nr_wait_function_trace = None
                self._nr_instance._nr_transaction = None
                self._nr_instance = None

        else:

            with fast_tracker.api.function_trace.FunctionTrace(
                    name='Request/Finish', group='Python/Twisted'):
                result = self._nr_next_object()

        return result


class ResourceRenderWrapper(object):

    def __init__(self, wrapped):
        if isinstance(wrapped, tuple):
            (instance, wrapped) = wrapped
        else:
            instance = None

        fast_tracker.api.object_wrapper.update_wrapper(self, wrapped)

        self._nr_instance = instance
        self._nr_next_object = wrapped

        if not hasattr(self, '_nr_last_object'):
            self._nr_last_object = wrapped

    def __get__(self, instance, klass):
        if instance is None:
            return self
        descriptor = self._nr_next_object.__get__(instance, klass)
        return self.__class__((instance, descriptor))

    def __call__(self, *args):

        if len(args) == 2:
            instance, request = args
        else:
            instance = self._nr_instance
            request = args[-1]

        assert instance != None

        transaction = fast_tracker.api.transaction.current_transaction()

        if transaction is None:
            return self._nr_next_object(*args)

        name = "%s.render_%s" % (
            fast_tracker.api.object_wrapper.callable_name(
                instance), request.method)
        transaction.set_transaction_name(name, priority=1)

        with fast_tracker.api.function_trace.FunctionTrace(name):
            return self._nr_next_object(*args)


class DeferredUserList(UserList.UserList):

    def pop(self, i=-1):
        import twisted.internet.defer
        item = super(DeferredUserList, self).pop(i)

        item0 = item[0]
        item1 = item[1]

        if item0[0] != twisted.internet.defer._CONTINUE:
            item0 = (fast_tracker.api.function_trace.FunctionTraceWrapper(
                item0[0], group='Python/Twisted/Callback'),
                     item0[1], item0[2])

        if item1[0] != twisted.internet.defer._CONTINUE:
            item1 = (fast_tracker.api.function_trace.FunctionTraceWrapper(
                item1[0], group='Python/Twisted/Errback'),
                     item1[1], item1[2])

        return item0, item1


class DeferredWrapper(object):

    def __init__(self, wrapped):
        if isinstance(wrapped, tuple):
            (instance, wrapped) = wrapped
        else:
            instance = None

        fast_tracker.api.object_wrapper.update_wrapper(self, wrapped)

        self._nr_instance = instance
        self._nr_next_object = wrapped

        if not hasattr(self, '_nr_last_object'):
            self._nr_last_object = wrapped

    def __get__(self, instance, klass):
        if instance is None:
            return self
        descriptor = self._nr_next_object.__get__(instance, klass)
        return self.__class__((instance, descriptor))

    def __call__(self, *args, **kwargs):

        self._nr_next_object(*args, **kwargs)

        if self._nr_instance:
            transaction = fast_tracker.api.transaction.current_transaction()
            if transaction:
                self._nr_instance._nr_transaction = transaction
                self._nr_instance.callbacks = DeferredUserList(
                    self._nr_instance.callbacks)


class DeferredCallbacksWrapper(object):

    def __init__(self, wrapped):
        if isinstance(wrapped, tuple):
            (instance, wrapped) = wrapped
        else:
            instance = None

        fast_tracker.api.object_wrapper.update_wrapper(self, wrapped)

        self._nr_instance = instance
        self._nr_next_object = wrapped

        if not hasattr(self, '_nr_last_object'):
            self._nr_last_object = wrapped

    def __get__(self, instance, klass):
        if instance is None:
            return self
        descriptor = self._nr_next_object.__get__(instance, klass)
        return self.__class__((instance, descriptor))

    def __call__(self):
        assert self._nr_instance != None

        transaction = fast_tracker.api.transaction.current_transaction()

        if transaction:
            return self._nr_next_object()

        if not hasattr(self._nr_instance, '_nr_transaction'):
            return self._nr_next_object()

        transaction = self._nr_instance._nr_transaction

        if not hasattr(transaction, '_nr_current_request'):
            return self._nr_next_object()
        request = transaction._nr_current_request()

        if not request:
            return self._nr_next_object()

        try:

            transaction.save_transaction()
            request._nr_is_deferred_callback = True
            if request._nr_wait_function_trace:
                request._nr_wait_function_trace.__exit__(None, None, None)
                request._nr_wait_function_trace = None

            else:
                _logger.debug('Called a Twisted.Web deferred when we were '
                              'not in a wait state.')

            with fast_tracker.api.error_trace.ErrorTrace():
                with fast_tracker.api.function_trace.FunctionTrace(
                        name='Deferred/Call',
                        group='Python/Twisted'):
                    return self._nr_next_object()

        finally:

            if request._nr_is_request_finished:
                transaction.__exit__(None, None, None)
                self._nr_instance._nr_transaction = None

            else:

                request._nr_wait_function_trace = \
                    fast_tracker.api.function_trace.FunctionTrace(
                        name='Deferred/Wait',
                        group='Python/Twisted')

                request._nr_wait_function_trace.__enter__()
                transaction.drop_transaction()

            request._nr_is_deferred_callback = False


class InlineGeneratorWrapper(object):

    def __init__(self, wrapped, generator):
        self._nr_wrapped = wrapped
        self._nr_generator = generator

    def __iter__(self):
        name = fast_tracker.api.object_wrapper.callable_name(self._nr_wrapped)
        iterable = iter(self._nr_generator)
        while 1:
            with fast_tracker.api.function_trace.FunctionTrace(
                    name, group='Python/Twisted/Generator'):
                yield next(iterable)


class InlineCallbacksWrapper(object):

    def __init__(self, wrapped):
        if isinstance(wrapped, tuple):
            (instance, wrapped) = wrapped
        else:
            instance = None

        fast_tracker.api.object_wrapper.update_wrapper(self, wrapped)

        self._nr_instance = instance
        self._nr_next_object = wrapped

        if not hasattr(self, '_nr_last_object'):
            self._nr_last_object = wrapped

    def __get__(self, instance, klass):
        if instance is None:
            return self
        descriptor = self._nr_next_object.__get__(instance, klass)
        return self.__class__((instance, descriptor))

    def __call__(self, *args, **kwargs):
        transaction = fast_tracker.api.transaction.current_transaction()

        if not transaction:
            return self._nr_next_object(*args, **kwargs)

        result = self._nr_next_object(*args, **kwargs)

        if not result:
            return result

        return iter(InlineGeneratorWrapper(self._nr_next_object, result))


def instrument_twisted_web_server(module):
    module.Request.process = RequestProcessWrapper(module.Request.process)


def instrument_twisted_web_http(module):
    module.Request.finish = RequestFinishWrapper(module.Request.finish)


def instrument_twisted_web_resource(module):
    module.Resource.render = ResourceRenderWrapper(module.Resource.render)


def instrument_twisted_internet_defer(module):
    module.Deferred.__init__ = DeferredWrapper(module.Deferred.__init__)
    module.Deferred._runCallbacks = DeferredCallbacksWrapper(
        module.Deferred._runCallbacks)


