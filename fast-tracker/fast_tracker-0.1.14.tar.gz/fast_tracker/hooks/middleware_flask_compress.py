# -*- coding: utf-8 -*-

import logging

from fast_tracker.api.html_insertion import insert_html_snippet
from fast_tracker.api.transaction import current_transaction
from fast_tracker.common.object_wrapper import wrap_function_wrapper

from fast_tracker.packages import six

_logger = logging.getLogger(__name__)

_boolean_states = {
    '1': True, 'yes': True, 'true': True, 'on': True,
    '0': False, 'no': False, 'false': False, 'off': False
}


def _setting_boolean(value):
    if value.lower() not in _boolean_states:
        raise ValueError('Not a boolean: %s' % value)
    return _boolean_states[value.lower()]


def _nr_wrapper_Compress_after_request(wrapped, instance, args, kwargs):
    def _params(response, *args, **kwargs):
        return response

    response = _params(*args, **kwargs)

    transaction = current_transaction()

    if not transaction:
        return wrapped(*args, **kwargs)

    if transaction.autorum_disabled:
        return wrapped(*args, **kwargs)

    if transaction.rum_header_generated:
        return wrapped(*args, **kwargs)
    ctype = (response.mimetype or '').lower()

    if 'Content-Encoding' in response.headers:
        return wrapped(*args, **kwargs)
    cdisposition = response.headers.get('Content-Disposition', '').lower()

    if cdisposition.split(';')[0].strip() == 'attachment':
        return wrapped(*args, **kwargs)

    header = transaction.browser_timing_header()

    if not header:
        return wrapped(*args, **kwargs)

    direct_passthrough = getattr(response, 'direct_passthrough', None)
    if direct_passthrough:
        if ctype == 'text/html':
            response.direct_passthrough = False
        else:
            return wrapped(*args, **kwargs)

    def html_to_be_inserted():
        return six.b(header) + six.b(transaction.browser_timing_footer())

    result = insert_html_snippet(response.get_data(), html_to_be_inserted)

    if result is not None:
        if transaction.settings.debug.log_autorum_middleware:
            _logger.debug('RUM insertion from flask_compress '
                          'triggered. Bytes added was %r.',
                          len(result) - len(response.get_data()))

        response.set_data(result)
        response.headers['Content-Length'] = str(len(response.get_data()))

    return wrapped(*args, **kwargs)


def instrument_flask_compress(module):
    wrap_function_wrapper(module, 'Compress.after_request',
                          _nr_wrapper_Compress_after_request)
