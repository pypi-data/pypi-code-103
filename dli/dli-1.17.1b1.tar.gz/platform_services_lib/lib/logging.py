#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#

import yaml
import logging
import logging.config
import os
from flask import current_app, request, g
from logging import Filter
from ddtrace.helpers import get_correlation_ids


suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


def human_memory_size(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


_UNSAFE_HEADERS = ['Authorization']


class DDTraceFilter(Filter):

    def filter(self, record):
        trace_id, span_id = get_correlation_ids()
        if trace_id and span_id:
            record.__dict__['dd.trace_id'] = str(trace_id)
            record.__dict__['dd.span_id'] = str(span_id)
        else:
            record.__dict__['dd.trace_id'] = 0
            record.__dict__['dd.span_id'] = 0

        if request and current_app:
            if record.levelno >= logging.ERROR:
                record.__dict__.update(get_request_data())
                record.__dict__.update(get_safe_headers())

            request_id = getattr(g, 'request_id', None)

            if request_id:
                record.__dict__['request_id'] = request_id

        return True


class ProcessMemoryInfoTraceFilter(Filter):

    def filter(self, record):
        # NOTE keep this import inside the function. We do not want to
        # reference psutil to make sure there is not a side-effect of starting
        # any profiling when it is disabled.
        import psutil
        current_thread = psutil.Process(os.getpid())
        # RSS: resident set size, the portion of memory occupied by
        # a process that is held in main memory
        record.thread_memory_usage = current_thread.memory_info().rss
        # Easier to read (harder to filter by)
        record.thread_memory_usage_human_readable = human_memory_size(
            record.thread_memory_usage
        )
        # NOTE thread_id is usually added to the logger via the formatter
        # but I want to do it all in the same place.
        record.process_id = current_thread.pid
        return True


# we need this due to the fact that some libraries - i.e. numpy,
# return locals with dict containing types as keys.
# `logging` cannot handle that and raises TypeError,
# that is handled internally, resulting in badly formatted logs.
class UnparsableNamespaceFilter(Filter):

    def filter(self, record):
        def _filter_out_unparsable_params(params):
            if not isinstance(params, dict):
                return params

            return {
                k: _filter_out_unparsable_params(v) for k, v in params.items()
                if isinstance(k, (str, int, float, bool)) or k is None
            }

        if hasattr(record, 'locals'):
            record.locals = _filter_out_unparsable_params(record.locals)
        return True


def get_safe_headers():
    # Remove headers that would compromise the user
    safe_headers = dict(request.headers)

    for header in _UNSAFE_HEADERS:
        if header in safe_headers:
            # Don't print entire secret. Allows us to filter by it
            safe_headers[header] = safe_headers[header][:15] + '****'

    return {
        'headers': safe_headers,
    }


def get_request_data():
    return {
        'method': request.method,
        'path': request.path,
        'host': request.host,
        # Request ID for logging between other services.
        'request_id': getattr(g, 'request_id', None)
    }


def setup_logging(
    config_path, level_override=logging.INFO,
    simple_formatter=False,
    pretty_json=False
):
    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    config['loggers']['']['level'] = level_override
    config['loggers']['api']['level'] = level_override
    config['loggers']['lib']['level'] = level_override
    config['loggers']['runner']['level'] = level_override
    config['loggers']['webapp']['level'] = level_override

    if simple_formatter:
        config['handlers']['info_handler']['formatter'] = 'simple'

    if pretty_json:
        config['formatters']['json_verbose']['json_indent'] = 4

    logging.config.dictConfig(config)
    logging.captureWarnings(True)
