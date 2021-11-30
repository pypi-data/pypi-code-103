# -*- coding: utf-8 -*-

import fast_tracker.core.trace_node

from fast_tracker.core.node_mixin import GenericNodeMixin


class FunctionNode(GenericNodeMixin):
    __slots__ = ['group', 'name', 'children', 'start_time', 'end_time', 'duration', 'exclusive', 'label',
                 'params', 'rollup',  'is_async', 'guid', 'agent_attributes', 'user_attributes',
                 'span_type', 'span_layer']

    def __init__(self, group, name, children, start_time, end_time, duration, exclusive, label,
                 params, rollup,  is_async, guid, agent_attributes, user_attributes,
                 span_type, span_layer):
        self.group = group
        self.name = name
        self.children = children
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.exclusive = exclusive
        self.label = label
        self.params = params
        self.rollup = rollup
        self.is_async = is_async
        self.guid = guid
        self.agent_attributes = agent_attributes
        self.user_attributes = user_attributes
        self.span_type = span_type
        self.span_layer = span_layer

    def trace_node(self, stats, root, connections):

        name = '%s/%s' % (self.group, self.name)

        name = root.string_table.cache(name)

        start_time = fast_tracker.core.trace_node.node_start_time(root, self)
        end_time = fast_tracker.core.trace_node.node_end_time(root, self)

        root.trace_node_count += 1

        children = []

        for child in self.children:
            if root.trace_node_count > root.trace_node_limit:
                break
            children.append(child.trace_node(stats, root, connections))

        params = self.get_trace_segment_params(
            root.settings, params=self.params)

        return fast_tracker.core.trace_node.TraceNode(start_time=start_time,
                                                      end_time=end_time, name=name, params=params, children=children,
                                                      label=self.label)

    def span_event(self, *args, **kwargs):
        base_attrs = kwargs.get('base_attrs', {})
        parent_guid = kwargs.get('parent_guid', None)
        transaction_node = kwargs.get('transaction_node', None)
        if transaction_node:
            component = transaction_node.root_component
        else:
            component = 'Python'
        operation = '/'.join([self.group, self.name])
        span = {
            't': self.span_type,
            's': self.guid,
            'd': int(self.duration * 1000),
            'ts': int(self.start_time * 1000),
            'te': int(self.end_time * 1000),
            'y': self.span_layer,
            'c': '.'.join([component, 'Function']),
            'o': operation,
            'er': 'False',
            'p': parent_guid,
            'g': {'operation': operation}
        }
        span.update(base_attrs)

        return span
