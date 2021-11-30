# -*- coding: utf-8 -*-

from fast_tracker.api.time_trace import record_exception
from fast_tracker.core.config import ignore_status_code
from fast_tracker.common.object_wrapper import wrap_function_wrapper


def should_ignore(exc, value, tb):
    from werkzeug.exceptions import HTTPException

    if isinstance(value, HTTPException):
        if ignore_status_code(value.code):
            return True


def _nr_wrap_Api_handle_error_(wrapped, instance, args, kwargs):
    resp = wrapped(*args, **kwargs)

    record_exception(ignore_errors=should_ignore)

    return resp


def instrument_flask_rest(module):
    wrap_function_wrapper(module, 'Api.handle_error',
                          _nr_wrap_Api_handle_error_)
