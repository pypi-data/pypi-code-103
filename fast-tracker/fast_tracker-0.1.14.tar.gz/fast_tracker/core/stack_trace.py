# -*- coding: utf-8 -*-
"""该模块解析Python异常栈
 直接用traceback包"""

import sys
import itertools

from fast_tracker.core.config import global_settings

_global_settings = global_settings()


def _format_stack_trace(frames):
    result = ['Traceback (most recent call last):']
    result.extend(['File "{source}", line {line}, in {name}'.format(**d)
            for d in frames])
    return result


def _extract_stack(f, skip, limit):
    if f is None:
        return []
    # 计算堆栈追踪
    n = 0
    l = []

    while f is not None and skip > 0:
        f = f.f_back
        skip -= 1

    while f is not None and n < limit:
        l.append(dict(source=f.f_code.co_filename,
                line=f.f_lineno, name=f.f_code.co_name))

        f = f.f_back
        n += 1

    l.reverse()

    return l


def current_stack(skip=0, limit=None):
    if limit is None:
        limit = _global_settings.max_stack_trace_lines

    try:
        raise ZeroDivisionError
    except ZeroDivisionError:
        f = sys.exc_info()[2].tb_frame.f_back

    return _format_stack_trace(_extract_stack(f, skip, limit))


def _extract_tb(tb, limit):
    if tb is None:
        return []

    n = 0
    top = tb

    while tb is not None:
        if n >= limit:
            top = top.tb_next

        tb = tb.tb_next
        n += 1
    n = 0
    l = []
    tb = top

    while tb is not None and n < limit:
        f = tb.tb_frame
        l.append(dict(source=f.f_code.co_filename,
                line=tb.tb_lineno, name=f.f_code.co_name))

        tb = tb.tb_next
        n += 1

    return l


def exception_stack(tb, limit=None):
    if tb is None:
        return []

    if limit is None:
        limit = _global_settings.max_stack_trace_lines  # TODO 最大展示异常栈行数

    _tb_stack = _extract_tb(tb, limit)

    if len(_tb_stack) < limit:
        _current_stack = _extract_stack(tb.tb_frame.f_back, skip=0,
                limit=limit-len(_tb_stack))
    else:
        _current_stack = []

    return _format_stack_trace(itertools.chain(_current_stack, _tb_stack))
