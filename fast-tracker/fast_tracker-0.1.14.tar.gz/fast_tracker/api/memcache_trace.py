# -*- coding: utf-8 -*-

import functools

from fast_tracker.common.async_wrapper import async_wrapper
from fast_tracker.api.time_trace import TimeTrace, current_trace
from fast_tracker.core.memcache_node import MemcacheNode
from fast_tracker.common.object_wrapper import FunctionWrapper, wrap_object
from fast_tracker.common.span_enum import SpanLayerAtrr, SpanType


class MemcacheTrace(TimeTrace):

    def __init__(self, command,
                 span_type=SpanType.Local.value,
                 span_layer=SpanLayerAtrr.CACHE.value, **kwargs):
        parent = None
        if kwargs:
            if len(kwargs) > 1:
                raise TypeError("无效参数:", kwargs)
            parent = kwargs['parent']
        super(MemcacheTrace, self).__init__(parent)

        self.command = command
        self.span_type = span_type
        self.span_layer = span_layer

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict(
                command=self.command))

    def terminal_node(self):
        return True

    def create_node(self):
        return MemcacheNode(
                command=self.command,
                children=self.children,
                start_time=self.start_time,
                end_time=self.end_time,
                duration=self.duration,
                exclusive=self.exclusive,
                is_async=self.is_async,
                guid=self.guid,
                agent_attributes=self.agent_attributes,
                user_attributes=self.user_attributes,
                span_layer=self.span_layer,
                span_type=self.span_type
        )


def MemcacheTraceWrapper(wrapped, command):

    def _nr_wrapper_memcache_trace_(wrapped, instance, args, kwargs):
        wrapper = async_wrapper(wrapped)
        if not wrapper:
            parent = current_trace()
            if not parent:
                return wrapped(*args, **kwargs)
        else:
            parent = None

        if callable(command):
            if instance is not None:
                _command = command(instance, *args, **kwargs)
            else:
                _command = command(*args, **kwargs)
        else:
            _command = command

        trace = MemcacheTrace(_command, parent=parent)

        if wrapper:
            return wrapper(wrapped, trace)(*args, **kwargs)

        with trace:
            return wrapped(*args, **kwargs)

    return FunctionWrapper(wrapped, _nr_wrapper_memcache_trace_)


def memcache_trace(command):
    return functools.partial(MemcacheTraceWrapper, command=command)


def wrap_memcache_trace(module, object_path, command):
    wrap_object(module, object_path, MemcacheTraceWrapper, (command,))
