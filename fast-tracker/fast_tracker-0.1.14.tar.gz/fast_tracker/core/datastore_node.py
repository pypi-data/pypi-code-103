# -*- coding: utf-8 -*-


import fast_tracker.core.trace_node

from fast_tracker.common import system_info
from fast_tracker.core.node_mixin import DatastoreNodeMixin


class DatastoreNode(DatastoreNodeMixin):
    __slots__ = ['product', 'target', 'operation', 'children', 'start_time', 'end_time', 'duration', 'exclusive',
                 'host', 'port_path_or_id', 'database_name', 'is_async', 'guid', 'agent_attributes',
                 'user_attributes', 'span_layer', 'span_type']

    def __init__(self, product, target, operation, children, start_time, end_time, duration, exclusive,
                 host, port_path_or_id, database_name, is_async, guid, agent_attributes,
                 user_attributes, span_layer, span_type):
        self.product = product
        self.target = target
        self.operation = operation
        self.children = children
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.exclusive = exclusive
        self.host = host
        self.port_path_or_id = port_path_or_id
        self.database_name = database_name
        self.is_async = is_async
        self.guid = guid
        self.agent_attributes = agent_attributes
        self.user_attributes = user_attributes
        self.span_layer = span_layer
        self.span_type = span_type

    @property
    def instance_hostname(self):
        if self.host in system_info.LOCALHOST_EQUIVALENTS:
            hostname = system_info.gethostname()
        else:
            hostname = self.host
        return hostname

    def trace_node(self, stats, root, connections):
        name = root.string_table.cache(self.name)

        start_time = fast_tracker.core.trace_node.node_start_time(root, self)
        end_time = fast_tracker.core.trace_node.node_end_time(root, self)

        children = []

        root.trace_node_count += 1
        self.agent_attributes['db.instance'] = self.db_instance
        params = self.get_trace_segment_params(root.settings)

        ds_tracer_settings = stats.settings.datastore_tracer
        instance_enabled = ds_tracer_settings.instance_reporting.enabled

        if instance_enabled:
            if self.instance_hostname:
                params['host'] = self.instance_hostname

            if self.port_path_or_id:
                params['port_path_or_id'] = self.port_path_or_id

        return fast_tracker.core.trace_node.TraceNode(start_time=start_time,
                                                      end_time=end_time, name=name, params=params, children=children,
                                                      label=None)

    def span_event(self, *args, **kwargs):
        component = self.product or self.target

        base_attrs = kwargs.get('base_attrs', {})
        tags = {'db_type': self.product, 'db_port': str(self.port_path_or_id),
                'db_host': self.host, 'db_instance': self.database_name}
        parent_guid = kwargs.get('parent_guid', None)
        span = {
            't': self.span_type,
            's': self.guid,
            'd': int(self.duration * 1000),
            'ts': int(self.start_time * 1000),
            'te': int(self.end_time * 1000),
            'y': self.span_layer,
            'c': component,
            'o': self.operation,
            'er': 'False',
            'r': self.host,
            'g': tags,
            'p': parent_guid
        }
        span.update(base_attrs)
        return span

