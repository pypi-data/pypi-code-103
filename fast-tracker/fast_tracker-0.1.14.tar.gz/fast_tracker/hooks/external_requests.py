# -*- coding: utf-8 -*-

import fast_tracker.api.external_trace


def instrument_requests_sessions(module):
    def url_request(obj, method, url, *args, **kwargs):
        return url

    def url_send(obj, request, *args, **kwargs):
        return request.url

    if hasattr(module.Session, 'send'):
        fast_tracker.api.external_trace.wrap_external_trace(
            module, 'Session.send', 'requests', url_send)

    else:
        if hasattr(module.Session, 'request'):
            fast_tracker.api.external_trace.wrap_external_trace(
                module, 'Session.request', 'requests', url_request)


def instrument_requests_api(module):
    def url_request(method, url, *args, **kwargs):
        return url

    if hasattr(module, 'request'):
        fast_tracker.api.external_trace.wrap_external_trace(
            module, 'request', 'requests', url_request)
