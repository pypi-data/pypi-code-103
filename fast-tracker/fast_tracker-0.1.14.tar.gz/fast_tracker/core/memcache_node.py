#  -*- coding: utf-8 -*-
import fast_tracker.core.trace_node

from fast_tracker.core.node_mixin import GenericNodeMixin


class MemcacheNode(GenericNodeMixin):
    __slots__ = ['command', 'children', 'start_time', 'end_time', 'duration', 'exclusive', 'is_async', 'guid',
                 'agent_attributes', 'user_attributes', 'span_type', 'span_layer']

    def __init__(self, command, children, start_time, end_time, duration, exclusive, is_async, guid,
                 agent_attributes, user_attributes, span_type, span_layer):
        self.command = command
        self.children = children
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.exclusive = exclusive
        self.is_async = is_async
        self.guid = guid
        self.agent_attributes = agent_attributes
        self.user_attributes = user_attributes
        self.span_type = span_type
        self.span_layer = span_layer

    @property
    def name(self):
        return 'Memcache/%s' % self.command

    def trace_node(self, stats, root, connections):
        name = root.string_table.cache(self.name)

        start_time = fast_tracker.core.trace_node.node_start_time(root, self)
        end_time = fast_tracker.core.trace_node.node_end_time(root, self)

        children = []

        root.trace_node_count += 1

        # Agent attributes
        params = self.get_trace_segment_params(root.settings)

        return fast_tracker.core.trace_node.TraceNode(start_time=start_time, end_time=end_time, name=name,
                                                      params=params, children=children, label=None)

    def span_event(self, *args, **kwargs):
        # TODO 待修改
        base_attrs = kwargs.get('base_attrs', {})
        parent_guid = kwargs.get('parent_guid', None)
        span = {
            't': self.span_type,
            's': self.guid,
            'd': int(self.duration * 1000),
            'ts': int(self.start_time * 1000),
            'te': int(self.end_time * 1000),
            'y': self.span_layer,
            'c': 'Memcache',
            'o': self.command,
            'er': 'True',
            'l': self.agent_attributes,
            'p': parent_guid
        }
        span.update(base_attrs)
        return span
