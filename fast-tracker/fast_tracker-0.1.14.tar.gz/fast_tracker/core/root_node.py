# -*- coding: utf-8 -*-
"""
根节点
"""

import fast_tracker.core.trace_node
from fast_tracker.core.node_mixin import GenericNodeMixin


class RootNode(GenericNodeMixin):
    __slots__ = ['name', 'children', 'start_time', 'end_time', 'exclusive',  'duration', 'guid', 'agent_attributes',
                 'user_attributes', 'path', 'trusted_parent_span', 'tracing_vendors', 'span_type', 'span_layer']

    def __init__(self, name, children, start_time, end_time, exclusive,  duration, guid, agent_attributes,
                 user_attributes, path, trusted_parent_span, tracing_vendors, span_type, span_layer):
        self.name = name
        self.children = children
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.exclusive = exclusive
        self.guid = guid
        self.agent_attributes = agent_attributes
        self.user_attributes = user_attributes
        self.span_type = span_type
        self.span_layer = span_layer
        self.path = path
        self.trusted_parent_span = trusted_parent_span
        self.tracing_vendors = tracing_vendors

    def span_event(self, *args, **kwargs):
        base_attrs = kwargs.get('base_attrs', {})
        transaction_node = kwargs.get('transaction_node', None)
        if transaction_node:
            tags, logs, host = transaction_node.root_span_agent_attributes()
            errors = transaction_node.errors
            component = transaction_node.root_component
        else:
            tags, logs, host = {}, {}, '0.0.0.0'
            errors = ()
            component = 'Python'
        span = {
            't': self.span_type,
            's': self.guid,
            'd': int(self.duration * 1000),
            'ts': int(self.start_time * 1000),
            'te': int(self.end_time * 1000),
            'y': self.span_layer,
            'c': component,
            'o': getattr(transaction_node, 'request_uri', self.name) if transaction_node else self.name,
            'er': 'False' if tags.get('status_code', '200') == '200' else 'True',
            'r': host,
            'g': tags
        }
        span.update(base_attrs)
        if errors:
            span['er'] = 'True'
            er = [{'Timestamp': int(error.timestamp * 1000),
                   'Data': {'event': 'error', 'error_kind': error.type,
                            'message': error.message, 'stack': '\r\n '.join(error.stack_trace)}}
                  for error in errors]
            span['l'] = er
        return span

    def trace_node(self, stats, root, connections):
        name = self.path
        start_time = fast_tracker.core.trace_node.node_start_time(root, self)
        end_time = fast_tracker.core.trace_node.node_end_time(root, self)
        root.trace_node_count += 1
        children = []
        for child in self.children:
            if root.trace_node_count > root.trace_node_limit:
                break
            children.append(child.trace_node(stats, root, connections))
        params = self.get_trace_segment_params(root.settings)

        return fast_tracker.core.trace_node.TraceNode(
            start_time=start_time,
            end_time=end_time,
            name=name,
            params=params,
            children=children,
            label=None)
