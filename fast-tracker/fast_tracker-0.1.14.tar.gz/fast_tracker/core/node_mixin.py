# -*- coding: utf-8 -*-
"""
混入设计模式
"""

import fast_tracker.core.attribute as attribute
from fast_tracker.core.attribute_filter import (DST_SPAN_EVENTS, DST_TRANSACTION_SEGMENTS)


class GenericNodeMixin(object):
    @property
    def processed_user_attributes(self):
        if hasattr(self, '_processed_user_attributes'):
            return self._processed_user_attributes
        self._processed_user_attributes = u_attrs = {}
        for k, v in self.user_attributes.items():
            k, v = attribute.process_user_attribute(k, v)
            u_attrs[k] = v
        return u_attrs

    def get_trace_segment_params(self, settings, params=None):
        _params = attribute.resolve_agent_attributes(
            self.agent_attributes,
            settings.attribute_filter,
            DST_TRANSACTION_SEGMENTS)

        if params:
            _params.update(params)

        _params.update(attribute.resolve_user_attributes(
            self.processed_user_attributes,
            settings.attribute_filter,
            DST_TRANSACTION_SEGMENTS))

        _params['exclusive_duration_millis'] = 1000.0 * self.exclusive
        return _params

    def span_event(
            self, settings, base_attrs=None, parent_guid=None, transaction_node=None):
       pass

    def span_events(self,
                    settings, base_attrs=None, parent_guid=None, transaction_node=None, count=1,
                    thread_id=0, thread_id_max_value=65535):
        if thread_id > 0:
            tid = transaction_node.thread_id % thread_id_max_value
        else:
            tid = thread_id_max_value
        guid = '%d.%d.%d' % (tid, int(self.start_time * 1000), count)
        self.guid = guid
        yield self.span_event(
            settings,
            base_attrs=base_attrs,
            parent_guid=parent_guid,
            transaction_node=transaction_node
        )
        count += 1
        for child in self.children:
            for event in child.span_events(
                    settings,
                    base_attrs=base_attrs,
                    parent_guid=self.guid,
                    transaction_node=transaction_node,
                    count=count,
                    thread_id=thread_id):
                yield event
                count += 1


class DatastoreNodeMixin(GenericNodeMixin):

    @property
    def name(self):
        product = self.product
        target = self.target
        operation = self.operation or 'other'

        if target:
            name = 'Datastore/statement/%s/%s/%s' % (product, target,
                                                     operation)
        else:
            name = 'Datastore/operation/%s/%s' % (product, operation)

        return name

    @property
    def db_instance(self):
        if hasattr(self, '_db_instance'):
            return self._db_instance

        db_instance_attr = None
        if self.database_name:
            _, db_instance_attr = attribute.process_user_attribute(
                'db.instance', self.database_name)

        self._db_instance = db_instance_attr
        return db_instance_attr

    def span_event(self, *args, **kwargs):
        pass
