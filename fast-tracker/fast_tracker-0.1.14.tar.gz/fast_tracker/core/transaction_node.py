# -*- coding: utf-8 -*-
"""
事物数据结构，事物是这个系统最终于的概念，每个Web 应用的Request请求或者非Web应用，都称为事物
"""

from collections import namedtuple
import random

import fast_tracker.core.error_collector
import fast_tracker.core.trace_node

from fast_tracker.core.string_table import StringTable
from fast_tracker.core.attribute import create_user_attributes
from fast_tracker.core.attribute_filter import (DST_ERROR_COLLECTOR,
                                                DST_TRANSACTION_TRACER, DST_TRANSACTION_EVENTS)
from fast_tracker.common.span_enum import SpanLayerAtrr, SpanType

_TransactionNode = namedtuple('_TransactionNode',
                              ['settings', 'path', 'type', 'group', 'base_name', 'name_for_metric',
                               'port', 'request_uri', 'queue_start', 'start_time',
                               'end_time', 'last_byte_time', 'response_time', 'total_time',
                               'duration', 'exclusive', 'root', 'errors', 'slow_sql',
                               'custom_events', 'suppress_apdex', 'custom_metrics', 'guid',
                               'cpu_time', 'suppress_transaction_trace', 'client_cross_process_id',
                               'referring_transaction_guid', 'record_tt', 'synthetics_resource_id',
                               'synthetics_job_id', 'synthetics_monitor_id', 'synthetics_header',
                               'is_part_of_cat', 'trip_id', 'path_hash', 'referring_path_hash',
                               'alternate_path_hashes', 'trace_intrinsics', 'agent_attributes',
                               'distributed_trace_intrinsics', 'user_attributes', 'priority',
                               'sampled', 'parent_transport_duration', 'parent_span', 'parent_type',
                               'parent_account', 'parent_app', 'parent_tx', 'parent_transport_type',
                               'root_span_guid', 'trace_id', 'loop_time', 'thread_id'])


class TransactionNode(_TransactionNode):
    """持有与交易根相对应的数据的类。 所有为交易记录的感兴趣的节点被保留为一棵树“children”属性中的结构。
    """

    def __new__(cls, *args, **kwargs):
        node = _TransactionNode.__new__(cls, *args, **kwargs)
        node.include_transaction_trace_request_uri = False
        return node

    def __hash__(self):
        return id(self)

    @property
    def string_table(self):
        result = getattr(self, '_string_table', None)
        if result is not None:
            return result
        self._string_table = StringTable()
        return self._string_table

    @property
    def name(self):
        return self.name_for_metric

    @property
    def root_component(self):
        if self.base_name:
            return self.base_name.split('.')[0].title()
        return 'Python'

    def error_details(self):

        if not self.errors:
            return

        for error in self.errors:
            params = {}
            params["stack_trace"] = error.stack_trace

            intrinsics = {'spanId': error.span_id}
            intrinsics.update(self.trace_intrinsics)
            params['intrinsics'] = intrinsics

            params['agentAttributes'] = {}
            for attr in self.agent_attributes:
                if attr.destinations & DST_ERROR_COLLECTOR:
                    params['agentAttributes'][attr.name] = attr.value

            params['userAttributes'] = {}
            for attr in self.user_attributes:
                if attr.destinations & DST_ERROR_COLLECTOR:
                    params['userAttributes'][attr.name] = attr.value

            err_attrs = create_user_attributes(error.custom_params,
                                               self.settings.attribute_filter)
            for attr in err_attrs:
                if attr.destinations & DST_ERROR_COLLECTOR:
                    params['userAttributes'][attr.name] = attr.value

            yield fast_tracker.core.error_collector.TracedError(
                start_time=error.timestamp,
                path=self.path,
                message=error.message,
                type=error.type,
                parameters=params)

    def transaction_trace(self, stats, limit, connections):

        self.trace_node_count = 0
        self.trace_node_limit = limit

        start_time = fast_tracker.core.trace_node.root_start_time(self)

        trace_node = self.root.trace_node(stats, self, connections)

        attributes = {}

        attributes['intrinsics'] = self.trace_intrinsics

        attributes['agentAttributes'] = {}
        for attr in self.agent_attributes:
            if attr.destinations & DST_TRANSACTION_TRACER:
                attributes['agentAttributes'][attr.name] = attr.value
                if attr.name == 'request.uri':
                    self.include_transaction_trace_request_uri = True

        attributes['userAttributes'] = {}
        for attr in self.user_attributes:
            if attr.destinations & DST_TRANSACTION_TRACER:
                attributes['userAttributes'][attr.name] = attr.value

        root = fast_tracker.core.trace_node.TraceNode(
            start_time=trace_node.start_time,
            end_time=trace_node.end_time,
            name='ROOT',
            params={},
            children=[trace_node],
            label=None)

        return fast_tracker.core.trace_node.RootNode(
            start_time=start_time,
            empty0={},
            empty1={},
            root=root,
            attributes=attributes)

    def slow_sql_nodes(self, stats):
        pass

    def transaction_event(self, stats_table):
        intrinsics = self.transaction_event_intrinsics(stats_table)

        user_attributes = {}
        for attr in self.user_attributes:
            if attr.destinations & DST_TRANSACTION_EVENTS:
                user_attributes[attr.name] = attr.value

        agent_attributes = {}
        for attr in self.agent_attributes:
            if attr.destinations & DST_TRANSACTION_EVENTS:
                agent_attributes[attr.name] = attr.value

        transaction_event = [intrinsics, user_attributes, agent_attributes]
        return transaction_event

    def transaction_event_intrinsics(self, stats_table):

        intrinsics = self._event_intrinsics(stats_table)

        intrinsics['type'] = 'Transaction'
        intrinsics['name'] = self.path
        intrinsics['totalTime'] = self.total_time

        def _add_if_not_empty(key, value):
            if value:
                intrinsics[key] = value

        if self.errors:
            intrinsics['error'] = True

        if self.path_hash:
            intrinsics['nr.guid'] = self.guid
            intrinsics['nr.tripId'] = self.trip_id
            intrinsics['nr.pathHash'] = self.path_hash

            _add_if_not_empty('nr.referringPathHash',
                              self.referring_path_hash)
            _add_if_not_empty('nr.alternatePathHashes',
                              ','.join(self.alternate_path_hashes))
            _add_if_not_empty('nr.referringTransactionGuid',
                              self.referring_transaction_guid)

        if self.synthetics_resource_id:
            intrinsics['nr.guid'] = self.guid

        if self.parent_tx:
            intrinsics['parentId'] = self.parent_tx

        if self.parent_span:
            intrinsics['parentSpanId'] = self.parent_span

        return intrinsics

    def error_events(self, stats_table):
        # TODO 暂时用不上
        errors = []
        for error in self.errors:

            intrinsics = self.error_event_intrinsics(error, stats_table)
            agent_attributes = {}
            for attr in self.agent_attributes:
                if attr.destinations & DST_ERROR_COLLECTOR:
                    agent_attributes[attr.name] = attr.value

            user_attributes = {}
            for attr in self.user_attributes:
                if attr.destinations & DST_ERROR_COLLECTOR:
                    user_attributes[attr.name] = attr.value

            err_attrs = create_user_attributes(error.custom_params,
                                               self.settings.attribute_filter)
            for attr in err_attrs:
                if attr.destinations & DST_ERROR_COLLECTOR:
                    user_attributes[attr.name] = attr.value

            error_event = [intrinsics, user_attributes, agent_attributes]
            errors.append(error_event)

        return errors

    def error_event_intrinsics(self, error, stats_table):

        intrinsics = self._event_intrinsics(stats_table)

        intrinsics['type'] = "TransactionError"
        intrinsics['error.class'] = error.type
        intrinsics['error.message'] = error.message
        intrinsics['transactionName'] = self.path
        intrinsics['spanId'] = error.span_id

        intrinsics['nr.transactionGuid'] = self.guid
        if self.referring_transaction_guid:
            guid = self.referring_transaction_guid
            intrinsics['nr.referringTransactionGuid'] = guid

        return intrinsics

    def _event_intrinsics(self, stats_table):

        cache = getattr(self, '_event_intrinsics_cache', None)
        if cache is not None:
            return self._event_intrinsics_cache.copy()

        intrinsics = self.distributed_trace_intrinsics.copy()

        intrinsics['timestamp'] = int(1000.0 * self.start_time)
        intrinsics['duration'] = self.response_time

        if self.port:
            intrinsics['port'] = self.port

        def _add_call_time(source, target):
            if (source, '') in stats_table:
                call_time = stats_table[(source, '')].total_call_time
                if target in intrinsics:
                    intrinsics[target] += call_time
                else:
                    intrinsics[target] = call_time

        def _add_call_count(source, target):

            if (source, '') in stats_table:
                call_count = stats_table[(source, '')].call_count
                if target in intrinsics:
                    intrinsics[target] += call_count
                else:
                    intrinsics[target] = call_count

        _add_call_time('WebFrontend/QueueTime', 'queueDuration')

        _add_call_time('External/all', 'externalDuration')
        _add_call_time('Datastore/all', 'databaseDuration')
        _add_call_time('Memcache/all', 'memcacheDuration')

        _add_call_count('External/all', 'externalCallCount')
        _add_call_count('Datastore/all', 'databaseCallCount')

        if self.loop_time:
            intrinsics['eventLoopTime'] = self.loop_time
        _add_call_time('EventLoop/Wait/all', 'eventLoopWait')

        self._event_intrinsics_cache = intrinsics.copy()

        return intrinsics

    def custom_details(self):
        """

        """
        if not self.custom_events:
            return []
        pq = self.custom_events.pq
        if not pq:
            return []
        for event in pq:
            if event[-1] is None:
                continue
            intrinsics, attributes = event[-1]
            operation_name = ''

            if 'operation_name' in attributes:
                operation_name = attributes.pop('operation_name')

            if hasattr(self.settings, 'thread_id_max_value'):
                thread_id_max_value = self.settings.thread_id_max_value
            else:
                thread_id_max_value = 65535
            tid = self.thread_id % thread_id_max_value
            guid = '%d.%d.%d' % (tid, int(self.start_time * 1000), random.randint(0, thread_id_max_value))
            yield {'id': self.trace_id,
                   'c': intrinsics['type'],
                   'ts': intrinsics['timestamp'],
                   'te': intrinsics['timestamp'],
                   'd': 1,
                   'p': self.root.guid,
                   's': guid,
                   'er': 'False',
                   'o': operation_name or intrinsics['type'],
                   't': SpanType.Local.value,
                   'y': SpanLayerAtrr.Local.value,
                   'g': attributes,
                   'l': intrinsics.get('logs', {})
                   }

    def root_span_agent_attributes(self):
        """

        :return:
        """
        agent_attributes = self.agent_attributes
        attributes = {}
        if not agent_attributes:
            return {}, {}
        for attr in agent_attributes:
            tmp = attr.name.split('.')
            if len(tmp) == 1:
                attributes[tmp[0]] = attr.value
            elif len(tmp) == 2:
                attributes[tmp[1]] = attr.value
            elif len(tmp) == 3:
                if not attributes.get(tmp[1]):
                    attributes[tmp[1]] = {}
                attributes[tmp[1]][tmp[2]] = attr.value
            else:
                pass
        try:
            host = attributes.get('headers', {}).get('host', '0.0.0.0')
        except:
            host = '0.0.0.0'
        tags = {'url': ''.join(['http://', host, self.request_uri]),  'path': self.request_uri,
                'http_method': attributes.get('method', ''), 'status_code': attributes.get('status', '')}
        return tags, {}, host

    def span_events(self, settings):
        base_attrs = {
            'id': self.trace_id
        }
        if hasattr(settings, 'thread_id_max_value'):
            thread_id_max_value = settings.thread_id_max_value
        else:
            thread_id_max_value = 65535
        for event in self.root.span_events(
                settings,
                base_attrs,
                parent_guid=self.parent_span,
                transaction_node=self,
                thread_id=self.thread_id,
                thread_id_max_value=thread_id_max_value
        ):
            yield event

        for event in self.custom_events:
            yield event
