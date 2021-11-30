# -*- coding: utf-8 -*-
from collections import namedtuple

import fast_tracker.core.attribute as attribute
import fast_tracker.core.trace_node

from fast_tracker.common import system_info
from fast_tracker.core.database_utils import sql_statement, explain_plan
from fast_tracker.core.node_mixin import DatastoreNodeMixin


_SlowSqlNode = namedtuple('_SlowSqlNode',
                          ['duration', 'path', 'request_uri', 'sql', 'sql_format',
                           'metric', 'dbapi2_module', 'stack_trace', 'connect_params',
                           'cursor_params', 'sql_parameters', 'execute_params',
                           'host', 'port_path_or_id', 'database_name', 'params'])


class SlowSqlNode(_SlowSqlNode):

    def __new__(cls, *args, **kwargs):
        node = _SlowSqlNode.__new__(cls, *args, **kwargs)
        node.statement = sql_statement(node.sql, node.dbapi2_module)
        return node

    @property
    def formatted(self):
        return self.statement.formatted(self.sql_format)

    @property
    def identifier(self):
        return self.statement.identifier


class DatabaseNode(DatastoreNodeMixin):
    __slots__ = ['dbapi2_module', 'sql', 'children', 'start_time', 'end_time', 'duration', 'exclusive', 'stack_trace',
                 'sql_format', 'connect_params', 'cursor_params', 'sql_parameters', 'execute_params', 'host',
                 'port_path_or_id', 'database_name', 'is_async', 'guid', 'agent_attributes', 'user_attributes',
                 'span_type', 'span_layer', 'statement']

    def __init__(self, dbapi2_module, sql, children, start_time, end_time, duration, exclusive, stack_trace,
                 sql_format, connect_params, cursor_params, sql_parameters, execute_params, host,
                 port_path_or_id, database_name, is_async, guid, agent_attributes, user_attributes,
                 span_type, span_layer):
        self.dbapi2_module = dbapi2_module
        self.sql = sql
        self.children = children
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.exclusive = exclusive
        self.stack_trace = stack_trace
        self.sql_format = sql_format
        self.connect_params = connect_params
        self.cursor_params = cursor_params
        self.sql_parameters = sql_parameters
        self.execute_params = execute_params
        self.host = host
        self.port_path_or_id = port_path_or_id
        self.database_name = database_name
        self.is_async = is_async
        self.guid = guid
        self.agent_attributes = agent_attributes
        self.user_attributes = user_attributes
        self.span_type = span_type
        self.span_layer = span_layer
        self.statement = sql_statement(sql, dbapi2_module)

    @property
    def product(self):
        return self.dbapi2_module and self.dbapi2_module._nr_database_product

    @property
    def instance_hostname(self):
        #  获取数据库实例的hostname
        if self.host in system_info.LOCALHOST_EQUIVALENTS:
            hostname = system_info.gethostname()
        else:
            hostname = self.host
        return hostname

    @property
    def operation(self):
        return self.statement.operation

    @property
    def target(self):
        # 获取操作目标的表
        return self.statement.target

    @property
    def formatted(self):
        return self.statement.formatted(self.sql_format)

    def explain_plan(self, connections):
        return explain_plan(connections, self.statement, self.connect_params,
                            self.cursor_params, self.sql_parameters, self.execute_params,
                            self.sql_format)

    def slow_sql_node(self, stats, root):
        """

        :param  stats:
        :param  fast_tracker.api.transaction.Transaction root:
        :return:
        """
        pass

    def trace_node(self, stats, root, connections):
        name = root.string_table.cache(self.name)

        start_time = fast_tracker.core.trace_node.node_start_time(root, self)
        end_time = fast_tracker.core.trace_node.node_end_time(root, self)

        children = []

        root.trace_node_count += 1

        sql = self.formatted

        self.agent_attributes['db.instance'] = self.db_instance
    
        if sql:
            limit = root.settings.agent_limits.sql_query_length_maximum
            self.agent_attributes['db.statement'] = sql[:limit]

        params = self.get_trace_segment_params(root.settings)

        if self.host:
            params['host'] = self.instance_hostname

        if self.port_path_or_id:
            params['port_path_or_id'] = self.port_path_or_id

        sql = params.get('db.statement')
        if sql:
            params['db.statement'] = root.string_table.cache(sql)

            if self.stack_trace:
                params['backtrace'] = [root.string_table.cache(x) for x in
                                       self.stack_trace]

            if getattr(self, 'generate_explain_plan', None):
                explain_plan_data = self.explain_plan(connections)
                if explain_plan_data:
                    params['explain_plan'] = explain_plan_data

        return fast_tracker.core.trace_node.TraceNode(start_time=start_time,
                                                      end_time=end_time, name=name, params=params, children=children,
                                                      label=None)

    def span_event(self, *args, **kwargs):
        if hasattr(self, 'dbapi2_module'):
            component = getattr(self.dbapi2_module, '__name__', None)
            if component is None:
                component = getattr(self.dbapi2_module, '__file__', None)
            if component is None:
                component = str(self.dbapi2_module)
        else:
            component = self.product or self.target

        sql = self.formatted
        if sql:
            _, sql = attribute.process_user_attribute(
                'db.statement', sql, max_length=2000, ending='...') 

        base_attrs = kwargs.get('base_attrs', {})
        tags = {'db_statement': sql, 'db_type': self.product, 'db_port': str(self.port_path_or_id),
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
            'er': 'False' if tags.get('status_code', '200') == '200' else 'True',
            'r': self.host,
            'g': tags,
            'p': parent_guid
        }
        span.update(base_attrs)
        if self.stack_trace:
            logs = {'stack': '\r\n '.join(self.stack_trace)}
            span['l'] = logs
        return span

