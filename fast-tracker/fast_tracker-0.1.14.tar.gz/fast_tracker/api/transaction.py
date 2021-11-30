# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import re
import sys
import time
import threading
import logging
import random
import weakref

import fast_tracker.packages.six as six

import fast_tracker.core.transaction_node
import fast_tracker.core.root_node
import fast_tracker.core.database_node
import fast_tracker.core.error_node

from fast_tracker.core.stats_engine import CustomMetrics, SampledDataSet
from fast_tracker.core.trace_cache import trace_cache
from fast_tracker.core.thread_utilization import utilization_tracker

from fast_tracker.core.attribute import (create_attributes,
                                         create_agent_attributes, create_user_attributes,
                                         process_user_attribute, MAX_NUM_USER_ATTRIBUTES)
from fast_tracker.core.attribute_filter import (DST_NONE, DST_ERROR_COLLECTOR,
                                                DST_TRANSACTION_TRACER)
from fast_tracker.core.config import DEFAULT_RESERVOIR_SIZE
from fast_tracker.core.custom_event import create_custom_event
from fast_tracker.core.stack_trace import exception_stack
from fast_tracker.common.encoding_utils import (generate_path_hash, obfuscate,
                                                deobfuscate, json_encode, json_decode, base64_decode,
                                                convert_to_cat_metadata_value, DistributedTracePayload, ensure_str,
                                                W3CTraceParent, W3CTraceState, NrTraceState)
from fast_tracker.common.span_enum import SpanType, SpanLayerAtrr
from fast_tracker.common.utils import seq_id

from fast_tracker.api.time_trace import TimeTrace

_logger = logging.getLogger(__name__)

DISTRIBUTED_TRACE_KEYS_REQUIRED = ('ty', 'ac', 'ap', 'tr', 'ti')
DISTRIBUTED_TRACE_TRANSPORT_TYPES = {'HTTP', 'HTTPS', 'Kafka', 'JMS', 'IronMQ', 'AMQP', 'Queue', 'Other'}
DELIMITER_FORMAT_RE = re.compile('[ \t]*,[ \t]*')
ACCEPTED_DISTRIBUTED_TRACE = 1
CREATED_DISTRIBUTED_TRACE = 2
PARENT_TYPE = {
    '0': 'App',
    '1': 'Browser',
    '2': 'Mobile',
}


class Sentinel(TimeTrace):
    def __init__(self, transaction):
        super(Sentinel, self).__init__(None)
        self.transaction = transaction
        self.thread_id = transaction.thread_id
        trace_cache().save_trace(self)

    def process_child(self, node, ignore_exclusive=False):
        if ignore_exclusive:
            self.children.append(node)
        else:
            return super(Sentinel, self).process_child(node)

    def drop_trace(self):
        trace_cache().drop_trace(self)

    @property
    def transaction(self):
        return self._transaction and self._transaction()

    @transaction.setter
    def transaction(self, value):
        if value:
            self._transaction = weakref.ref(value)

    @property
    def root(self):
        return self

    @root.setter
    def root(self, value):
        pass


class CachedPath(object):
    def __init__(self, transaction):
        self._name = None
        self.transaction = weakref.ref(transaction)

    def path(self):
        if self._name is not None:
            return self._name

        transaction = self.transaction()
        if transaction:
            return transaction.path

        return 'Unknown'


class Transaction(object):
    STATE_PENDING = 0
    STATE_RUNNING = 1
    STATE_STOPPED = 2

    def __init__(self, application, enabled=None):

        self._application = application

        self.thread_id = None

        self._transaction_id = id(self)
        self._transaction_lock = threading.Lock()

        self._dead = False

        self._state = self.STATE_PENDING
        self._settings = None

        self._name_priority = 0
        self._group = None
        self._name = None
        self._cached_path = CachedPath(self)
        self._loop_time = 0.0

        self._frameworks = set()

        self._frozen_path = None

        self.root_span = None

        self._request_uri = None
        self._port = None

        self.queue_start = 0.0

        self.start_time = 0.0
        self.end_time = 0.0
        self.last_byte_time = 0.0

        self.total_time = 0.0

        self.stopped = False

        self._trace_node_count = 0

        self._errors = []
        self._slow_sql = []
        self._custom_events = SampledDataSet(capacity=DEFAULT_RESERVOIR_SIZE)

        self._stack_trace_count = 0
        self._explain_plan_count = 0

        self._string_cache = {}

        self._custom_params = {}
        self._request_params = {}

        self._utilization_tracker = None

        self._thread_utilization_start = None
        self._thread_utilization_end = None
        self._thread_utilization_value = None

        self._cpu_user_time_start = None
        self._cpu_user_time_end = None
        self._cpu_user_time_value = 0.0

        self._read_length = None

        self._read_start = None
        self._read_end = None

        self._sent_start = None
        self._sent_end = None

        self._bytes_read = 0
        self._bytes_sent = 0

        self._calls_read = 0
        self._calls_readline = 0
        self._calls_readlines = 0

        self._calls_write = 0
        self._calls_yield = 0

        self._transaction_metrics = {}

        self._agent_attributes = {}

        self.background_task = False

        self.enabled = False
        self.autorum_disabled = False

        self.ignore_transaction = False
        self.suppress_apdex = False
        self.suppress_transaction_trace = False

        self.capture_params = None

        self.rum_token = None

        trace_id = seq_id()  # TODO trace_id的入口
        self.guid = ''
        self._trace_id = trace_id

        self.parent_type = None
        self.parent_span = None
        self.trusted_parent_span = None
        self.tracing_vendors = None
        self.parent_tx = None
        self.parent_app = None
        self.parent_account = None
        self.parent_transport_type = None
        self.parent_transport_duration = None
        self.tracestate = ''
        self._priority = None
        self._sampled = None

        self._distributed_trace_state = 0

        self.client_cross_process_id = None
        self.client_account_id = None
        self.client_application_id = None
        self.referring_transaction_guid = None
        self.record_tt = False
        self._trip_id = None
        self._referring_path_hash = None
        self._alternate_path_hashes = {}
        self.is_part_of_cat = False

        self.synthetics_resource_id = None
        self.synthetics_job_id = None
        self.synthetics_monitor_id = None
        self.synthetics_header = None

        self._custom_metrics = CustomMetrics()

        self._profile_frames = {}
        self._profile_skip = 1
        self._profile_count = 0

        global_settings = application.global_settings

        if global_settings.enabled:
            if enabled or (enabled is None and application.enabled):
                self._settings = application.settings
                if not self._settings:
                    application.activate()
                    self._settings = application.settings

                if self._settings:
                    self.enabled = True

    def __del__(self):
        self._dead = True
        if self._state == self.STATE_RUNNING:
            self.__exit__(None, None, None)

    def __enter__(self):

        assert (self._state == self.STATE_PENDING)

        if not self.enabled:
            return self

        self.start_time = time.time()

        self._cpu_user_time_start = os.times()[0]
        self.thread_id = trace_cache().current_thread_id()

        if (not hasattr(sys, '_current_frames') or
                self.thread_id in sys._current_frames()):
            thread_instance = threading.currentThread()
            self._utilization_tracker = utilization_tracker(
                self.application.name)
            if self._utilization_tracker:
                self._utilization_tracker.enter_transaction(thread_instance)
                self._thread_utilization_start = \
                    self._utilization_tracker.utilization_count()
        self.root_span = Sentinel(self)
        self._state = self.STATE_RUNNING

        return self

    def __exit__(self, exc, value, tb):

        if not self.enabled:
            return

        if self._transaction_id != id(self):
            return

        if not self._settings:
            return
        root = self.root_span
        root.drop_trace()

        self._state = self.STATE_STOPPED

        if exc is not None and value is not None and tb is not None:
            root.record_exception((exc, value, tb))
        if not self.stopped:
            self.end_time = time.time()

        duration = self.end_time - self.start_time
        if self.last_byte_time == 0.0:
            response_time = duration
        else:
            response_time = self.last_byte_time - self.start_time

        if not self._cpu_user_time_end:
            self._cpu_user_time_end = os.times()[0]

        if duration and self._cpu_user_time_end:
            self._cpu_user_time_value = (self._cpu_user_time_end -
                                         self._cpu_user_time_start)

        if self._utilization_tracker:
            self._utilization_tracker.exit_transaction()
            if self._thread_utilization_start is not None and duration > 0.0:
                if not self._thread_utilization_end:
                    self._thread_utilization_end = (
                        self._utilization_tracker.utilization_count())
                self._thread_utilization_value = (
                                                         self._thread_utilization_end -
                                                         self._thread_utilization_start) / duration

        exclusive = duration + root.exclusive

        root_node = fast_tracker.core.root_node.RootNode(
            name=self.name_for_metric,
            children=root.children,
            start_time=self.start_time,
            end_time=self.end_time,
            exclusive=exclusive,
            duration=duration,
            guid=root.guid,
            agent_attributes=root.agent_attributes,
            user_attributes=root.user_attributes,
            path=self.path,
            trusted_parent_span=self.trusted_parent_span,
            tracing_vendors=self.tracing_vendors,
            span_type=SpanType.Entry.value,
            span_layer=SpanLayerAtrr.HTTP.value
        )

        self.total_time += exclusive

        self._freeze_path()

        if self._sent_start:
            if not self._sent_end:
                self._sent_end = time.time()

        if self.client_cross_process_id is not None:
            metric_name = 'ClientApplication/%s/all' % (
                self.client_cross_process_id)
            self.record_custom_metric(metric_name, duration)

        for key, value in six.iteritems(self._transaction_metrics):
            self.record_custom_metric(key, {'count': value})

        if self._frameworks:
            for framework, version in self._frameworks:
                self.record_custom_metric('Python/Framework/%s/%s' %
                                          (framework, version), 1)

        if self._settings.distributed_tracing.enabled:
            self._compute_sampled_and_priority()

        self._cached_path._name = self.path
        node = fast_tracker.core.transaction_node.TransactionNode(
            settings=self._settings,
            path=self.path,
            type=self.type,
            group=self.group_for_metric,
            base_name=self._name,
            name_for_metric=self.name_for_metric,
            port=self._port,
            request_uri=self._request_uri,
            queue_start=self.queue_start,
            start_time=self.start_time,
            end_time=self.end_time,
            last_byte_time=self.last_byte_time,
            total_time=self.total_time,
            response_time=response_time,
            duration=duration,
            exclusive=exclusive,
            errors=tuple(self._errors),
            slow_sql=tuple(self._slow_sql),
            custom_events=self._custom_events,
            suppress_apdex=self.suppress_apdex,
            custom_metrics=self._custom_metrics,
            guid=self.guid,
            cpu_time=self._cpu_user_time_value,
            suppress_transaction_trace=self.suppress_transaction_trace,
            client_cross_process_id=self.client_cross_process_id,
            referring_transaction_guid=self.referring_transaction_guid,
            record_tt=self.record_tt,
            synthetics_resource_id=self.synthetics_resource_id,
            synthetics_job_id=self.synthetics_job_id,
            synthetics_monitor_id=self.synthetics_monitor_id,
            synthetics_header=self.synthetics_header,
            is_part_of_cat=self.is_part_of_cat,
            trip_id=self.trip_id,
            path_hash=self.path_hash,
            referring_path_hash=self._referring_path_hash,
            alternate_path_hashes=self.alternate_path_hashes,
            trace_intrinsics=self.trace_intrinsics,
            distributed_trace_intrinsics=self.distributed_trace_intrinsics,
            agent_attributes=self.agent_attributes,
            user_attributes=self.user_attributes,
            priority=self.priority,
            sampled=self.sampled,
            parent_span=self.parent_span,
            parent_transport_duration=self.parent_transport_duration,
            parent_type=self.parent_type,
            parent_account=self.parent_account,
            parent_app=self.parent_app,
            parent_tx=self.parent_tx,
            parent_transport_type=self.parent_transport_type,
            root_span_guid=root.guid,
            trace_id=self.trace_id,
            loop_time=self._loop_time,
            root=root_node,
            thread_id=self.thread_id
        )
        self._settings = None
        self.enabled = False
        if not self.ignore_transaction:
            self._application.record_transaction(node)

    @property
    def sampled(self):
        return self._sampled

    @property
    def priority(self):
        return self._priority

    @property
    def state(self):
        return self._state

    @property
    def is_distributed_trace(self):
        return self._distributed_trace_state != 0

    @property
    def settings(self):
        return self._settings

    @property
    def application(self):
        return self._application

    @property
    def type(self):
        if self.background_task:
            transaction_type = 'OtherTransaction'
        else:
            transaction_type = 'WebTransaction'
        return transaction_type

    @property
    def name(self):
        return self._name

    @property
    def group(self):
        return self._group

    @property
    def name_for_metric(self):
        group = self.group_for_metric

        transaction_name = self._name

        if transaction_name is None:
            transaction_name = '<undefined>'

        if (group in ('Uri', 'NormalizedUri') and
                transaction_name.startswith('/')):
            name = '%s%s' % (group, transaction_name)
        else:
            name = '%s/%s' % (group, transaction_name)

        return name

    @property
    def group_for_metric(self):
        _group = self._group

        if _group is None:
            if self.background_task:
                _group = 'Python'
            else:
                _group = 'Uri'

        return _group

    @property
    def path(self):
        if self._frozen_path:
            return self._frozen_path

        return '%s/%s' % (self.type, self.name_for_metric)

    @property
    def trip_id(self):
        return self._trip_id or self.guid

    @property
    def trace_id(self):
        return self._trace_id

    @property
    def alternate_path_hashes(self):

        return sorted(set(self._alternate_path_hashes.values()) -
                      set([self.path_hash]))

    @property
    def path_hash(self):

        if not self.is_part_of_cat:
            return None

        identifier = '%s;%s' % (self.application.name, self.path)

        if self._alternate_path_hashes.get(identifier):
            return self._alternate_path_hashes[identifier]

        try:
            seed = int((self._referring_path_hash or '0'), base=16)
        except Exception:
            seed = 0

        path_hash = generate_path_hash(identifier, seed)

        if len(self._alternate_path_hashes) < 10:
            self._alternate_path_hashes[identifier] = path_hash

        return path_hash

    @property
    def attribute_filter(self):
        return self._settings.attribute_filter

    @property
    def read_duration(self):
        read_duration = 0
        if self._read_start and self._read_end:
            read_duration = self._read_end - self._read_start
        return read_duration

    @property
    def sent_duration(self):
        sent_duration = 0
        if self._sent_start and self._sent_end:
            sent_duration = self._sent_end - self._sent_start
        return sent_duration

    @property
    def queue_wait(self):
        queue_wait = 0
        if self.queue_start:
            queue_wait = self.start_time - self.queue_start
            if queue_wait < 0:
                queue_wait = 0
        return queue_wait

    @property
    def should_record_segment_params(self):
        # Only record parameters when it is safe to do so
        return (self.settings and
                not self.settings.high_security)

    @property
    def trace_intrinsics(self):
        i_attrs = {}

        if self.referring_transaction_guid:
            i_attrs['referring_transaction_guid'] = \
                self.referring_transaction_guid
        if self.client_cross_process_id:
            i_attrs['client_cross_process_id'] = self.client_cross_process_id
        if self.trip_id:
            i_attrs['trip_id'] = self.trip_id
        if self.path_hash:
            i_attrs['path_hash'] = self.path_hash
        if self.synthetics_resource_id:
            i_attrs['synthetics_resource_id'] = self.synthetics_resource_id
        if self.synthetics_job_id:
            i_attrs['synthetics_job_id'] = self.synthetics_job_id
        if self.synthetics_monitor_id:
            i_attrs['synthetics_monitor_id'] = self.synthetics_monitor_id
        if self.total_time:
            i_attrs['totalTime'] = self.total_time
        if self._loop_time:
            i_attrs['eventLoopTime'] = self._loop_time

        i_attrs.update(self.distributed_trace_intrinsics)

        return i_attrs

    @property
    def distributed_trace_intrinsics(self):
        #  分布式链路上下文参数
        i_attrs = {}

        if not self._settings.distributed_tracing.enabled:
            return i_attrs

        i_attrs['guid'] = self.guid
        i_attrs['sampled'] = self.sampled
        i_attrs['priority'] = self.priority
        i_attrs['traceId'] = self.trace_id

        if not self._distributed_trace_state:
            return i_attrs

        if self.parent_type:
            i_attrs['parent.type'] = self.parent_type
        if self.parent_account:
            i_attrs['parent.account'] = self.parent_account
        if self.parent_app:
            i_attrs['parent.app'] = self.parent_app
        if self.parent_transport_type:
            i_attrs['parent.transportType'] = self.parent_transport_type
        if self.parent_transport_duration:
            i_attrs['parent.transportDuration'] = \
                self.parent_transport_duration
        if self.trusted_parent_span:
            i_attrs['trustedParentId'] = self.trusted_parent_span
        if self.tracing_vendors:
            i_attrs['tracingVendors'] = self.tracing_vendors

        return i_attrs

    @property
    def request_parameters_attributes(self):

        attributes_request = []

        if (self.capture_params is None) or self.capture_params:

            if self._request_params:

                r_attrs = {}

                for k, v in self._request_params.items():
                    new_key = 'request.parameters.%s' % k
                    new_val = ",".join(v)

                    final_key, final_val = process_user_attribute(new_key,
                                                                  new_val)

                    if final_key:
                        r_attrs[final_key] = final_val

                if self.capture_params is None:
                    attributes_request = create_attributes(r_attrs,
                                                           DST_NONE, self.attribute_filter)
                elif self.capture_params:
                    attributes_request = create_attributes(r_attrs,
                                                           DST_ERROR_COLLECTOR | DST_TRANSACTION_TRACER,
                                                           self.attribute_filter)

        return attributes_request

    def _add_agent_attribute(self, key, value):
        self._agent_attributes[key] = value

    @property
    def agent_attributes(self):
        a_attrs = self._agent_attributes

        agent_attributes = create_agent_attributes(a_attrs, self.attribute_filter)
        agent_attributes.extend(self.request_parameters_attributes)

        return agent_attributes

    @property
    def user_attributes(self):
        return create_user_attributes(self._custom_params,
                                      self.attribute_filter)

    def _compute_sampled_and_priority(self):
        if self._priority is None:
            self._priority = float('%.6f' % random.random())

        if self._sampled is None:
            self._sampled = self._application.compute_sampled()
            if self._sampled:
                self._priority += 1

    def _freeze_path(self):
        if self._frozen_path is None:
            self._name_priority = None

            if self._group == 'Uri' and self._name != '/':
                name, ignore = self._application.normalize_name(
                    self._name, 'url')

                if self._name != name:
                    self._group = 'NormalizedUri'
                    self._name = name

                self.ignore_transaction = self.ignore_transaction or ignore

            path, ignore = self._application.normalize_name(
                self.path, 'transaction')

            self.ignore_transaction = self.ignore_transaction or ignore

            self._frozen_path, ignore = self._application.normalize_name(
                path, 'segment')

            self.ignore_transaction = self.ignore_transaction or ignore

    def _create_distributed_trace_data_with_guid(self, guid):
        data = self._create_distributed_trace_data()
        if guid and data and 'id' in data:
            data['id'] = guid
        return data

    def _create_distributed_trace_data(self):
        if not self.enabled:
            return

        settings = self._settings
        account_id = settings.account_id
        trusted_account_key = settings.trusted_account_key
        application_id = settings.primary_application_id
        if not settings.distributed_tracing.enabled:
            return

        self._compute_sampled_and_priority()
        data = dict(
            ty='App',
            ac=account_id,
            ap=application_id,
            tr=self.trace_id,
            sa=self.sampled,
            pr=self.priority,
            tx=self.guid,
            ti=int(time.time() * 1000.0),
        )

        if account_id != trusted_account_key:
            data['tk'] = trusted_account_key

        current_span = trace_cache().current_trace()
        if (settings.span_events.enabled and
                settings.collect_span_events and
                current_span and self.sampled):
            data['id'] = current_span.guid

        self._distributed_trace_state |= CREATED_DISTRIBUTED_TRACE

        return data

    def _create_distributed_trace_payload(self):
        try:
            data = self._create_distributed_trace_data()
            if data is None:
                return
            payload = DistributedTracePayload(
                v=DistributedTracePayload.version,
                d=data,
            )
        except:
            pass
        else:
            return payload

    def create_distributed_trace_payload(self):
        return self._create_distributed_trace_payload()

    def _generate_distributed_trace_headers(self, data=None):
        try:
            data = data or self._create_distributed_trace_data()
            if data:
                traceparent = W3CTraceParent(data).text()
                yield ("traceparent", traceparent)

                tracestate = NrTraceState(data).text()
                if self.tracestate:
                    tracestate += ',' + self.tracestate
                yield ("tracestate", tracestate)

                if (not self._settings.
                        distributed_tracing.exclude_fast_header):
                    payload = DistributedTracePayload(
                        v=DistributedTracePayload.version,
                        d=data,
                    )
                    yield ('fast', payload.http_safe())

        except:
            pass

    def insert_distributed_trace_headers(self, headers):
        headers.extend(self._generate_distributed_trace_headers())

    def _can_accept_distributed_trace_headers(self):
        if not self.enabled:
            return False

        settings = self._settings
        if not settings.distributed_tracing.enabled:
            return False

        if self._distributed_trace_state:
            return False

        return True

    def _accept_distributed_trace_payload(
            self, payload, transport_type='HTTP'):
        if not payload:
            return False

        payload = DistributedTracePayload.decode(payload)
        if not payload:
            return False

        try:
            version = payload.get('v')
            major_version = version and int(version[0])

            if major_version is None:
                return False

            if major_version > DistributedTracePayload.version[0]:
                return False

            data = payload.get('d', {})
            if not all(k in data for k in DISTRIBUTED_TRACE_KEYS_REQUIRED):
                return False

            # Must have either id or tx
            if not any(k in data for k in ('id', 'tx')):
                return False

            settings = self._settings
            try:
                data['ti'] = int(data['ti'])
            except:
                return False

            if 'pr' in data:
                try:
                    data['pr'] = float(data['pr'])
                except:
                    data['pr'] = None

            self._accept_distributed_trace_data(data, transport_type)
            return True

        except:
            return False

    def accept_distributed_trace_payload(self, *args, **kwargs):
        if not self._can_accept_distributed_trace_headers():
            return False
        return self._accept_distributed_trace_payload(*args, **kwargs)

    def _accept_distributed_trace_data(self, data, transport_type):
        if transport_type not in DISTRIBUTED_TRACE_TRANSPORT_TYPES:
            transport_type = 'Unknown'

        self.parent_transport_type = transport_type

        self.parent_type = data.get('ty')

        self.parent_span = data.get('id')
        self.parent_tx = data.get('tx')
        self.parent_app = data.get('ap')
        self.parent_account = data.get('ac')

        self._trace_id = data.get('tr')

        priority = data.get('pr')
        if priority is not None:
            self._priority = priority
            self._sampled = data.get('sa')

        if 'ti' in data:
            transport_start = data['ti'] / 1000.0

            now = time.time()
            if transport_start > now:
                self.parent_transport_duration = 0.0
            else:
                self.parent_transport_duration = now - transport_start

        self._distributed_trace_state = ACCEPTED_DISTRIBUTED_TRACE

    def accept_distributed_trace_headers(self, headers, transport_type='HTTP'):
        if not self._can_accept_distributed_trace_headers():
            return False

        try:
            traceparent = headers.get('traceparent', '')
            tracestate = headers.get('tracestate', '')
            distributed_header = headers.get('fast', '')
        except Exception:
            traceparent = ''
            tracestate = ''
            distributed_header = ''

            for k, v in headers:
                k = ensure_str(k)
                if k == 'traceparent':
                    traceparent = v
                elif k == 'tracestate':
                    tracestate = v
                elif k == 'fast':
                    distributed_header = v

        if traceparent:
            try:
                traceparent = ensure_str(traceparent).strip()
                data = W3CTraceParent.decode(traceparent)
            except:
                data = None

            if not data:
                return False

            if tracestate:
                tracestate = ensure_str(tracestate)
                try:
                    vendors = W3CTraceState.decode(tracestate)
                    tk = self._settings.trusted_account_key
                    payload = vendors.pop(tk + '@nr', '')
                    self.tracing_vendors = ','.join(vendors.keys())
                    self.tracestate = vendors.text(limit=31)
                except:
                    pass
                else:
                    if payload:
                        try:
                            tracestate_data = NrTraceState.decode(payload, tk)
                        except:
                            tracestate_data = None
                        if tracestate_data:
                            self.trusted_parent_span = \
                                tracestate_data.pop('id', None)
                            data.update(tracestate_data)
            self._accept_distributed_trace_data(data, transport_type)
            return True
        elif distributed_header:
            distributed_header = ensure_str(distributed_header)
            return self._accept_distributed_trace_payload(
                distributed_header,
                transport_type)

    def _process_incoming_cat_headers(self, encoded_cross_process_id,
                                      encoded_txn_header):
        settings = self._settings

        if not self.enabled:
            return

        if not (settings.cross_application_tracer.enabled and
                settings.cross_process_id and settings.encoding_key):
            return

        if encoded_cross_process_id is None:
            return

        try:
            client_cross_process_id = deobfuscate(
                encoded_cross_process_id, settings.encoding_key)
            client_account_id, client_application_id = \
                map(int, client_cross_process_id.split('#'))
            self.client_cross_process_id = client_cross_process_id
            self.client_account_id = client_account_id
            self.client_application_id = client_application_id

            txn_header = json_decode(deobfuscate(
                encoded_txn_header,
                settings.encoding_key))

            if txn_header:
                self.is_part_of_cat = True
                self.referring_transaction_guid = txn_header[0]

                self.record_tt = (self.record_tt or
                                  txn_header[1])

                if isinstance(txn_header[2], six.string_types):
                    self._trip_id = txn_header[2]
                if isinstance(txn_header[3], six.string_types):
                    self._referring_path_hash = txn_header[3]
        except Exception:
            pass

    def _generate_response_headers(self, read_length=None):
        nr_headers = []

        if self.client_cross_process_id is not None:

            if self.queue_start:
                queue_time = self.start_time - self.queue_start
            else:
                queue_time = 0

            if self.end_time:
                duration = self.end_time - self.start_time
            else:
                duration = time.time() - self.start_time

            self._freeze_path()

            if read_length is None:
                read_length = self._read_length

            read_length = read_length if read_length is not None else -1

            payload = (self._settings.cross_process_id, self.path, queue_time,
                       duration, read_length, self.guid, self.record_tt)
            app_data = json_encode(payload)

            nr_headers.append(('X-fast-App-Data', obfuscate(
                app_data, self._settings.encoding_key)))

        return nr_headers

    def get_response_metadata(self):
        nr_headers = dict(self._generate_response_headers())
        return convert_to_cat_metadata_value(nr_headers)

    def process_request_metadata(self, cat_linking_value):
        try:
            payload = base64_decode(cat_linking_value)
        except:
            return

        nr_headers = json_decode(payload)
        encoded_cross_process_id = nr_headers.get('X-fast-ID')
        encoded_txn_header = nr_headers.get('X-fast-Transaction')
        return self._process_incoming_cat_headers(encoded_cross_process_id,
                                                  encoded_txn_header)

    def set_transaction_name(self, name, group=None, priority=None):

        if self._name_priority is None:
            return

        if priority is not None and priority < self._name_priority:
            return

        if priority is not None:
            self._name_priority = priority
        if isinstance(name, bytes):
            name = name.decode('Latin-1')
        group = group or 'Function'

        if group.startswith('/'):
            group = 'Function' + group

        self._group = group
        self._name = name

    def record_exception(self, exc=None, value=None, tb=None,
                         params={}, ignore_errors=[]):
        current_span = trace_cache().current_trace()
        if current_span:
            current_span.record_exception(
                (exc, value, tb),
                params=params,
                ignore_errors=ignore_errors)

    def _create_error_node(self, settings, fullname, message,
                           custom_params, span_id, tb):

        if not settings.error_collector.enabled:
            return

        if not settings.collect_errors and not settings.collect_error_events:
            return

        if len(self._errors) >= settings.agent_limits.errors_per_transaction:
            return

        for error in self._errors:
            if error.type == fullname and error.message == message:
                return

        node = fast_tracker.core.error_node.ErrorNode(
            timestamp=time.time(),
            type=fullname,
            message=message,
            span_id=span_id,
            stack_trace=exception_stack(tb),
            custom_params=custom_params,
            file_name=None,
            line_number=None,
            source=None)

        self._errors.append(node)

    def record_custom_metric(self, name, value):
        pass

    def record_custom_metrics(self, metrics):
        pass

    def record_custom_event(self, event_type, params):
        settings = self._settings

        if not settings:
            return

        if not settings.custom_insights_events.enabled:
            return

        event = create_custom_event(event_type, params)
        if event:
            self._custom_events.add(event, priority=self.priority)

    def _intern_string(self, value):
        return self._string_cache.setdefault(value, value)

    def _process_node(self, node):
        self._trace_node_count += 1
        node.node_count = self._trace_node_count
        self.total_time += node.exclusive

        if type(node) is fast_tracker.core.database_node.DatabaseNode:
            settings = self._settings
            if not settings.collect_traces:
                return
            if (not settings.slow_sql.enabled and
                    not settings.transaction_tracer.explain_enabled):
                return
            if settings.transaction_tracer.record_sql == 'off':
                return
            if node.duration < settings.transaction_tracer.explain_threshold:
                return
            self._slow_sql.append(node)

    def stop_recording(self):
        if not self.enabled:
            return

        if self.stopped:
            return

        if self.end_time:
            return

        self.end_time = time.time()
        self.stopped = True

        if self._utilization_tracker:
            if self._thread_utilization_start:
                if not self._thread_utilization_end:
                    self._thread_utilization_end = (
                        self._utilization_tracker.utilization_count())

        self._cpu_user_time_end = os.times()[0]

    def add_custom_parameter(self, name, value):
        if not self._settings:
            return False

        if self._settings.high_security:
            _logger.debug('在高安全模式下不能添加自定义参数.')
            return False

        if len(self._custom_params) >= MAX_NUM_USER_ATTRIBUTES:
            _logger.debug('自定义属性已经达到最大限度,删除一些属性. 删除属性: %r=%r', name, value)
            return False

        key, val = process_user_attribute(name, value)

        if key is None:
            return False
        else:
            self._custom_params[key] = val
            return True

    def add_custom_parameters(self, items):
        result = True

        for name, value in items:
            result &= self.add_custom_parameter(name, value)

        return result

    def add_framework_info(self, name, version=None):
        if name:
            self._frameworks.add((name, version))

    def dump(self, file):

        print('Application: %s' % (self.application.name), file=file)
        print('Time Started: %s' % (
            time.asctime(time.localtime(self.start_time))), file=file)
        print('Thread Id: %r' % (self.thread_id), file=file)
        print('Current Status: %d' % (self._state), file=file)
        print('Recording Enabled: %s' % (self.enabled), file=file)
        print('Ignore Transaction: %s' % (self.ignore_transaction), file=file)
        print('Transaction Dead: %s' % (self._dead), file=file)
        print('Transaction Stopped: %s' % (self.stopped), file=file)
        print('Background Task: %s' % (self.background_task), file=file)
        print('Request URI: %s' % (self._request_uri), file=file)
        print('Transaction Group: %s' % (self._group), file=file)
        print('Transaction Name: %s' % (self._name), file=file)
        print('Name Priority: %r' % (self._name_priority), file=file)
        print('Frozen Path: %s' % (self._frozen_path), file=file)
        print('AutoRUM Disabled: %s' % (self.autorum_disabled), file=file)


def current_transaction(active_only=True):
    current = trace_cache().current_transaction()
    if active_only:
        if current and (current.ignore_transaction or current.stopped):
            return None
    return current


def set_transaction_name(name, group=None, priority=None):
    transaction = current_transaction()
    if transaction:
        transaction.set_transaction_name(name, group, priority)


def end_of_transaction():
    transaction = current_transaction()
    if transaction:
        transaction.stop_recording()


def set_background_task(flag=True):
    transaction = current_transaction()
    if transaction:
        transaction.background_task = flag


def ignore_transaction(flag=True):
    transaction = current_transaction()
    if transaction:
        transaction.ignore_transaction = flag


def suppress_apdex_metric(flag=True):
    transaction = current_transaction()
    if transaction:
        transaction.suppress_apdex = flag


def capture_request_params(flag=True):
    transaction = current_transaction()
    if transaction and transaction.settings:
        if transaction.settings.high_security:
            _logger.warn("在高安全模式下不能添加自定义参数.")
        else:
            transaction.capture_params = flag


def add_custom_parameter(key, value):
    transaction = current_transaction()
    if transaction:
        return transaction.add_custom_parameter(key, value)
    else:
        return False


def add_custom_parameters(items):
    transaction = current_transaction()
    if transaction:
        return transaction.add_custom_parameters(items)
    else:
        return False


def add_framework_info(name, version=None):
    transaction = current_transaction()
    if transaction:
        transaction.add_framework_info(name, version)


def get_browser_timing_header():
    transaction = current_transaction()
    if transaction and hasattr(transaction, 'browser_timing_header'):
        return transaction.browser_timing_header()
    return ''


def get_browser_timing_footer():
    transaction = current_transaction()
    if transaction and hasattr(transaction, 'browser_timing_footer'):
        return transaction.browser_timing_footer()
    return ''


def disable_browser_autorum(flag=True):
    transaction = current_transaction()
    if transaction:
        transaction.autorum_disabled = flag


def suppress_transaction_trace(flag=True):
    transaction = current_transaction()
    if transaction:
        transaction.suppress_transaction_trace = flag


def record_custom_metric(name, value, application=None):
    pass


def record_custom_metrics(metrics, application=None):
    pass


def record_custom_event(event_type, params, application=None):
    if application is None:
        transaction = current_transaction()
        if transaction:
            transaction.record_custom_event(event_type, params)
        else:
            _logger.debug('record_custom_event 已经被调用,但是没有事物在运行. 结果以下事务不会被收集.'
                          ' event_type: %r params: %r..', event_type, params)
    elif application.enabled:
        application.record_custom_event(event_type, params)


def accept_distributed_trace_payload(payload, transport_type='HTTP'):
    transaction = current_transaction()
    if transaction:
        return transaction.accept_distributed_trace_payload(payload,
                                                            transport_type)
    return False


def accept_distributed_trace_headers(headers, transport_type='HTTP'):
    transaction = current_transaction()
    if transaction:
        return transaction.accept_distributed_trace_headers(
            headers,
            transport_type)


def create_distributed_trace_payload():
    transaction = current_transaction()
    if transaction:
        return transaction.create_distributed_trace_payload()


def insert_distributed_trace_headers(headers):
    transaction = current_transaction()
    if transaction:
        return transaction.insert_distributed_trace_headers(headers)


def current_trace_id():
    transaction = current_transaction()
    if transaction:
        return transaction.trace_id


def current_span_id():
    trace = trace_cache().current_trace()
    if trace:
        return trace.guid
