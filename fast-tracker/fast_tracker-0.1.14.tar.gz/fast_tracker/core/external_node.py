# -*- coding: utf-8 -*-
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import fast_tracker.core.attribute as attribute
import fast_tracker.core.trace_node

from fast_tracker.core.node_mixin import GenericNodeMixin


class ExternalNode(GenericNodeMixin):
    __slots__ = ['library', 'url', 'method', 'children', 'start_time', 'end_time', 'duration', 'exclusive',
                 'params', 'is_async', 'guid', 'agent_attributes', 'user_attributes', 'span_type', 'span_layer']

    def __init__(self,library, url, method, children, start_time, end_time, duration, exclusive,
                 params, is_async, guid, agent_attributes, user_attributes, span_type, span_layer):
        self.library = library
        self.url = url
        self.method = method
        self.children = children
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.exclusive = exclusive
        self.params = params
        self.is_async = is_async
        self.guid = guid
        self.agent_attributes = agent_attributes
        self.user_attributes = user_attributes
        self.span_type = span_type
        self.span_layer = span_layer
    
    @property
    def details(self):
        if hasattr(self, '_details'):
            return self._details

        try:
            self._details = urlparse.urlparse(self.url or '')
        except Exception:
            self._details = urlparse.urlparse('http://unknown.url')

        return self._details

    @property
    def name(self):
        return 'External/%s/%s/%s' % (
            self.netloc, self.library, self.method or '')

    @property
    def url_with_path(self):
        details = self.details
        url = urlparse.urlunsplit((details.scheme, details.netloc,
                                   details.path, '', ''))
        return url

    @property
    def http_url(self):
        if hasattr(self, '_http_url'):
            return self._http_url

        _, url_attr = attribute.process_user_attribute(
            'http_url', self.url_with_path)
        self._http_url = url_attr
        return url_attr

    @property
    def netloc(self):
        hostname = self.details.hostname or 'unknown'

        try:
            scheme = self.details.scheme.lower()
            port = self.details.port
        except Exception:
            scheme = None
            port = None

        if (scheme, port) in (('http', 80), ('https', 443)):
            port = None

        netloc = port and ('%s:%s' % (hostname, port)) or hostname
        return netloc

    def trace_node(self, stats, root, connections):

        netloc = self.netloc

        method = self.method or ''

        if self.cross_process_id is None:
            name = 'External/%s/%s/%s' % (netloc, self.library, method)
        else:
            name = 'ExternalTransaction/%s/%s/%s' % (netloc, self.cross_process_id, self.external_txn_name)
        name = root.string_table.cache(name)
        start_time = fast_tracker.core.trace_node.node_start_time(root, self)
        end_time = fast_tracker.core.trace_node.node_end_time(root, self)
        children = []
        root.trace_node_count += 1
        self.agent_attributes['http.url'] = self.http_url
        params = self.get_trace_segment_params(root.settings, params=self.params)
        return fast_tracker.core.trace_node.TraceNode(start_time=start_time,  end_time=end_time, name=name,
                                                      params=params, children=children, label=None)

    def span_event(self, *args, **kwargs):
        base_attrs = kwargs.get('base_attrs', {})
        parent_guid = kwargs.get('parent_guid', None)
        tags = {}
        if self.method:
            tags['http_method'] = self.method
        if self.agent_attributes and isinstance(self.agent_attributes, dict):
            tags['http_method'] = self.agent_attributes.get('http_method')
            tags['status_code'] = self.agent_attributes.get('status_code', '200')
        tags['url'] = self.http_url
        tags['path'] = self.details.path
        span = {
            't': self.span_type,
            's': self.guid,
            'd': int(self.duration * 1000),
            'ts': int(self.start_time * 1000),
            'te': int(self.end_time * 1000),
            'y': self.span_layer,
            'c': attribute.process_user_attribute('component', self.library)[-1].title(),
            'o': self.name,
            'er': 'False' if tags.get('status_code', '200') == '200' else 'True',
            'r': self.netloc,
            'g': tags,
            'p': parent_guid
        }
        span.update(base_attrs)
        return span
