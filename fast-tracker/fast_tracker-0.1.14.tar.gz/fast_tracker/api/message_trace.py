# -*- coding: utf-8 -*-

import functools

from fast_tracker.common.async_wrapper import async_wrapper
from fast_tracker.api.cat_header_mixin import CatHeaderMixin
from fast_tracker.api.time_trace import TimeTrace, current_trace
from fast_tracker.common.object_wrapper import FunctionWrapper, wrap_object
from fast_tracker.core.message_node import MessageNode
from fast_tracker.common.span_enum import SpanType, SpanLayerAtrr


class MessageTrace(CatHeaderMixin, TimeTrace):

    cat_id_key = 'fastID'
    cat_transaction_key = 'fastTransaction'
    cat_appdata_key = 'fastAppData'
    cat_synthetics_key = 'fastSynthetics'

    def __init__(self, library, operation, destination_type, destination_name, params=None,
                 span_type=SpanType.Local.value,
                 span_layer=SpanLayerAtrr.MQ.value,
                 **kwargs):

        parent = None
        if kwargs:
            if len(kwargs) > 1:
                raise TypeError("无效参数:", kwargs)
            parent = kwargs['parent']
        super(MessageTrace, self).__init__(parent)

        self.library = library
        self.operation = operation

        self.params = params

        self.destination_type = destination_type
        self.destination_name = destination_name
        self.span_type = span_type
        self.span_layer = span_layer

    def __enter__(self):
        result = super(MessageTrace, self).__enter__()

        if result and self.transaction:
            self.library = self.transaction._intern_string(self.library)
            self.operation = self.transaction._intern_string(self.operation)

        if not (self.should_record_segment_params and self.settings and
                self.settings.message_tracer.segment_parameters_enabled):
            self.params = None
        return result

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict(
                library=self.library, operation=self.operation))

    def terminal_node(self):
        return True

    def create_node(self):
        return MessageNode(
                library=self.library,
                operation=self.operation,
                children=self.children,
                start_time=self.start_time,
                end_time=self.end_time,
                duration=self.duration,
                exclusive=self.exclusive,
                destination_name=self.destination_name,
                destination_type=self.destination_type,
                params=self.params,
                is_async=self.is_async,
                guid=self.guid,
                agent_attributes=self.agent_attributes,
                user_attributes=self.user_attributes,
                span_type=self.span_type,
                span_layer=self.span_layer
        )


def MessageTraceWrapper(wrapped, library, operation, destination_type, destination_name, params={}):

    def _nr_message_trace_wrapper_(wrapped, instance, args, kwargs):
        wrapper = async_wrapper(wrapped)
        if not wrapper:
            parent = current_trace()
            if not parent:
                return wrapped(*args, **kwargs)
        else:
            parent = None

        if callable(library):
            if instance is not None:
                _library = library(instance, *args, **kwargs)
            else:
                _library = library(*args, **kwargs)
        else:
            _library = library

        if callable(operation):
            if instance is not None:
                _operation = operation(instance, *args, **kwargs)
            else:
                _operation = operation(*args, **kwargs)
        else:
            _operation = operation

        if callable(destination_type):
            if instance is not None:
                _destination_type = destination_type(instance, *args, **kwargs)
            else:
                _destination_type = destination_type(*args, **kwargs)
        else:
            _destination_type = destination_type

        if callable(destination_name):
            if instance is not None:
                _destination_name = destination_name(instance, *args, **kwargs)
            else:
                _destination_name = destination_name(*args, **kwargs)
        else:
            _destination_name = destination_name

        trace = MessageTrace(_library, _operation,
                _destination_type, _destination_name, params={}, parent=parent)

        if wrapper:
            return wrapper(wrapped, trace)(*args, **kwargs)

        with trace:
            return wrapped(*args, **kwargs)

    return FunctionWrapper(wrapped, _nr_message_trace_wrapper_)


def message_trace(library, operation, destination_type, destination_name, params={}):
    return functools.partial(MessageTraceWrapper, library=library, operation=operation,
                             destination_type=destination_type, destination_name=destination_name, params=params)


def wrap_message_trace(module, object_path, library, operation, destination_type, destination_name, params={}):
    wrap_object(module, object_path, MessageTraceWrapper,
                (library, operation, destination_type, destination_name, params))
