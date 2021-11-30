# -*- coding: utf-8 -*-

import sys

import fast_tracker.packages.six as six

import fast_tracker.api.transaction
import fast_tracker.api.object_wrapper
import fast_tracker.api.external_trace
from fast_tracker.common.span_enum import SpanType, SpanLayerAtrr


class capture_external_trace(object):

    def __init__(self, wrapped):
        fast_tracker.api.object_wrapper.update_wrapper(self, wrapped)
        self._nr_next_object = wrapped
        if not hasattr(self, '_nr_last_object'):
            self._nr_last_object = wrapped

    def __call__(self, url, *args, **kwargs):

        if not isinstance(url, six.string_types):
            return self._nr_next_object(url, *args, **kwargs)

        parsed_url = url

        if parsed_url.startswith('feed:http'):
            parsed_url = parsed_url[5:]
        elif parsed_url.startswith('feed:'):
            parsed_url = 'http:' + url[5:]

        if parsed_url.split(':')[0].lower() in ['http', 'https', 'ftp']:
            current_transaction = fast_tracker.api.transaction.current_transaction()
            if current_transaction:
                trace = fast_tracker.api.external_trace.ExternalTrace(
                    'feedparser', parsed_url, 'GET', span_type=SpanType.Exit.value, span_layer=SpanLayerAtrr.HTTP.value)
                context_manager = trace.__enter__()
                try:
                    result = self._nr_next_object(url, *args, **kwargs)
                except:  # Catch all
                    context_manager.__exit__(*sys.exc_info())
                    raise
                context_manager.__exit__(None, None, None)
                return result
            else:
                return self._nr_next_object(url, *args, **kwargs)
        else:
            return self._nr_next_object(url, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._nr_next_object, name)


def instrument(module):
    fast_tracker.api.object_wrapper.wrap_object(
        module, 'parse', capture_external_trace)
