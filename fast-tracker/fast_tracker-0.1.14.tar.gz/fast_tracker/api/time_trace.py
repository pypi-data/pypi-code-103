# -*- coding: utf-8 -*-

import logging
import random
import time
import sys
import fast_tracker.packages.six as six
import traceback
from fast_tracker.core.trace_cache import trace_cache
from fast_tracker.core.attribute import (
    process_user_attribute, MAX_NUM_USER_ATTRIBUTES)

_logger = logging.getLogger(__name__)


class TimeTrace(object):

    def __init__(self, parent=None):
        self.parent = parent
        self.root = None
        self.child_count = 0
        self.children = []
        self.start_time = 0.0
        self.end_time = 0.0
        self.duration = 0.0
        self.exclusive = 0.0
        self.thread_id = None
        self.activated = False
        self.exited = False
        self.is_async = False
        self.has_async_children = False
        self.min_child_start_time = float('inf')
        self.exc_data = (None, None, None)
        self.should_record_segment_params = False
        self.guid = ''
        self.agent_attributes = {}
        self.user_attributes = {}

    @property
    def transaction(self):
        return self.root and self.root.transaction

    @property
    def settings(self):
        transaction = self.transaction
        return transaction and transaction.settings

    def _is_leaf(self):
        return self.child_count == len(self.children)

    def __enter__(self):
        self.parent = parent = self.parent or current_trace()
        if not parent:
            return self
        if parent.exited or parent.terminal_node():
            self.parent = None
            return parent

        transaction = parent.root.transaction

        if transaction.stopped or not transaction.enabled:
            self.parent = None
            return self

        parent.increment_child_count()

        self.root = parent.root
        self.should_record_segment_params = (
            transaction.should_record_segment_params)

        self.start_time = time.time()

        cache = trace_cache()
        self.thread_id = cache.current_thread_id()

        try:
            cache.save_trace(self)
        except:
            self.parent = None
            raise

        self.activated = True

        return self

    def __exit__(self, exc, value, tb):
        if not self.parent:
            return

        if not self.activated:
            _logger.error('Runtime instrumentation error. The __exit__() '
                          'method of %r was called prior to __enter__() being '
                          'called. Report this issue to FAST support.\n%s',
                          self, ''.join(traceback.format_stack()[:-1]))

            return

        transaction = self.root.transaction

        if not transaction:
            return

        if transaction.stopped:
            self.end_time = transaction.end_time
        else:
            self.end_time = time.time()

        if self.end_time < self.start_time:
            self.end_time = self.start_time
        self.duration = self.end_time - self.start_time

        self.exclusive += self.duration

        if self.exclusive < 0:
            self.exclusive = 0

        self.exited = True

        self.exc_data = (exc, value, tb)

        if self._ready_to_complete():
            self._complete_trace()
        else:
            trace_cache().pop_current(self)

    def add_custom_attribute(self, key, value):
        settings = self.settings
        if not settings:
            return

        if settings.high_security:
            _logger.debug('在高安全模式下不能添加自定义参数.')
            return

        if len(self.user_attributes) >= MAX_NUM_USER_ATTRIBUTES:
            _logger.debug('自定义属性已经达到最大限度,删除一些属性: %r=%r', key, value)
            return

        self.user_attributes[key] = value

    def record_exception(self, exc_info=None,
                         params={}, ignore_errors=[]):

        transaction = self.transaction
        settings = transaction and transaction.settings

        if not settings:
            return
        if exc_info and None not in exc_info:
            exc, value, tb = exc_info
        else:
            exc, value, tb = sys.exc_info()
        if exc is None or value is None or tb is None:
            return

        should_ignore = None

        if hasattr(transaction, '_ignore_errors'):
            should_ignore = transaction._ignore_errors(exc, value, tb)
            if should_ignore:
                return

        if callable(ignore_errors):
            should_ignore = ignore_errors(exc, value, tb)
            if should_ignore:
                return

        module = value.__class__.__module__
        name = value.__class__.__name__

        if should_ignore is None:
            if module:
                names = ('%s:%s' % (module, name), '%s.%s' % (module, name))
            else:
                names = name

            for fullname in names:
                if not callable(ignore_errors) and fullname in ignore_errors:
                    return

                if fullname in settings.error_collector.ignore_errors:
                    return

            fullname = names[0]

        else:
            if module:
                fullname = '%s:%s' % (module, name)
            else:
                fullname = name
        custom_params = {}

        if settings.high_security:
            if params:
                _logger.debug('在高安全模式下不能添加自定义参数.')
        else:
            try:
                for k, v in params.items():
                    name, val = process_user_attribute(k, v)
                    if name:
                        custom_params[name] = val
            except Exception:
                _logger.debug('未知原因导致参数检验失败.正在删除错误参数: %r.', fullname, exc_info=True)
                custom_params = {}

        if (settings.strip_exception_messages.enabled and
                fullname not in settings.strip_exception_messages.whitelist):
            message = '\'strip_exception_messages\'被移除'
        else:
            try:
                message = six.text_type(value)

            except Exception:
                try:
                    message = str(value)

                except Exception:
                    message = '<unprintable %s object>' % type(value).__name__
        self._add_agent_attribute('error.class', fullname)
        self._add_agent_attribute('error.message', message)

        transaction._create_error_node(
            settings, fullname, message, custom_params, self.guid, tb)

    def _add_agent_attribute(self, key, value):
        self.agent_attributes[key] = value

    def _force_exit(self, exc, value, tb):
        self.child_count = len(self.children)
        return self.__exit__(exc, value, tb)

    def _ready_to_complete(self):
        if not self.exited:
            return False
        if len(self.children) != self.child_count:
            return False

        return True

    def complete_trace(self):
        if self._ready_to_complete():
            self._complete_trace()

    def _complete_trace(self):
        if self.parent is None:
            _logger.error('运行时检测到错误.事务已经完成,这意味着完整的链路跟踪完成. 追踪信息: %r \n%s',
                          self, ''.join(traceback.format_stack()[:-1]))

            return

        parent = self.parent
        if parent.exited or parent.has_async_children:
            self.is_async = True

        trace_cache().pop_current(self)
        self.parent = None
        transaction = self.root.transaction
        self.root = None
        exc_data = self.exc_data
        self.exc_data = (None, None, None)
        self.finalize_data(transaction, *exc_data)
        exc_data = None
        node = self.create_node()

        if node:
            transaction._process_node(node)
            parent.process_child(node)
        parent.complete_trace()

    def finalize_data(self, transaction, exc=None, value=None, tb=None):
        pass

    def create_node(self):
        return self

    def terminal_node(self):
        return False

    def update_async_exclusive_time(self, min_child_start_time,
                                    exclusive_duration):
        if self.exited and (self.end_time < min_child_start_time):
            exclusive_delta = 0.0
        elif self.exited:
            exclusive_delta = (self.end_time -
                               min_child_start_time)
            min_child_start_time = self.end_time
        else:
            exclusive_delta = exclusive_duration
        self.exclusive -= exclusive_delta
        exclusive_duration_remaining = exclusive_duration - exclusive_delta

        if self.parent and exclusive_duration_remaining > 0.0:
            self.parent.update_async_exclusive_time(min_child_start_time,
                                                    exclusive_duration_remaining)

    def process_child(self, node):
        self.children.append(node)
        if node.is_async:
            self.min_child_start_time = min(self.min_child_start_time,
                                            node.start_time)

            if self.child_count == len(self.children):
                exclusive_duration = node.end_time - self.min_child_start_time

                self.update_async_exclusive_time(self.min_child_start_time,
                                                 exclusive_duration)

                self.min_child_start_time = float('inf')
        else:
            self.exclusive -= node.duration

    def increment_child_count(self):
        self.child_count += 1

        if (self.child_count - len(self.children)) > 1:
            self.has_async_children = True
        else:
            self.has_async_children = False

    def get_linking_metadata(self):
        metadata = {
            "entity.type": "SERVICE",
        }
        txn = self.transaction
        if txn:
            metadata["span.id"] = self.guid
            metadata["trace.id"] = txn.trace_id
            settings = txn.settings
            if settings:
                metadata["entity.name"] = settings.app_name
                entity_guid = settings.entity_guid
                if entity_guid:
                    metadata["entity.guid"] = entity_guid
        return metadata


def add_custom_span_attribute(key, value):
    trace = current_trace()
    if trace:
        trace.add_custom_attribute(key, value)


def current_trace():
    return trace_cache().current_trace()


def get_linking_metadata():
    trace = current_trace()
    if trace:
        return trace.get_linking_metadata()
    else:
        return {
            "entity.type": "SERVICE",
        }


def record_exception(exc=None, value=None, tb=None, params={},
                     ignore_errors=[], application=None):
    if application is None:
        trace = current_trace()
        if trace:
            trace.record_exception((exc, value, tb), params,
                                   ignore_errors)
    else:
        if application.enabled:
            application.record_exception(exc, value, tb, params,
                                         ignore_errors)
