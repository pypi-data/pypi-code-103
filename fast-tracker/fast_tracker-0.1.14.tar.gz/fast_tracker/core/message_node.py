# -*- coding: utf-8 -*-
from collections import namedtuple

import fast_tracker.core.trace_node

from fast_tracker.core.node_mixin import GenericNodeMixin
from fast_tracker.common.span_enum import SpanType, SpanLayerAtrr


class MessageNode(GenericNodeMixin):
    __slots__ = ['library', 'operation', 'children', 'start_time', 'end_time', 'duration', 'exclusive',
                 'destination_name', 'destination_type', 'params', 'is_async', 'guid', 'agent_attributes',
                 'user_attributes', 'span_type', 'span_layer']

    def __init__(self, library, operation, children, start_time, end_time, duration, exclusive,
                 destination_name, destination_type, params, is_async, guid, agent_attributes,
                 user_attributes, span_type, span_layer):
        self.library = library
        self.operation = operation
        self.children = children
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.exclusive = exclusive
        self.destination_name = destination_name
        self.destination_type = destination_type
        self.params = params
        self.is_async = is_async
        self.guid = guid
        self.agent_attributes = agent_attributes
        self.user_attributes = user_attributes
        self.span_type = span_type
        self.span_layer = span_layer

    @property
    def name(self):
        name = 'MessageBroker/%s/%s/%s/Named/%s' % (self.library,
                                                    self.destination_type, self.operation, self.destination_name)
        return name

    def trace_node(self, stats, root, connections):
        name = root.string_table.cache(self.name)
        start_time = fast_tracker.core.trace_node.node_start_time(root, self)
        end_time = fast_tracker.core.trace_node.node_end_time(root, self)
        children = []
        root.trace_node_count += 1
        params = self.get_trace_segment_params(
            root.settings, params=self.params)
        return fast_tracker.core.trace_node.TraceNode(start_time=start_time, end_time=end_time, name=name,
                                                      params=params, children=children, label=None)

    def span_event(self, *args, **kwargs):
        base_attrs = kwargs.get('base_attrs', {})
        parent_guid = kwargs.get('parent_guid', None)
        span = {
            't': self.span_type,
            's': self.guid,
            'd': int(self.duration * 1000),
            'ts': int(self.start_time * 1000),
            'te': int(self.end_time * 1000),
            'y': self.span_layer,
            'c': self.library,
            'o': self.operation,
            'er': 'True',
            'g': {'message_destination': self.destination_name, 'message_destination_type': self.destination_type},
            'p': parent_guid
        }
        span.update(base_attrs)
        return span
