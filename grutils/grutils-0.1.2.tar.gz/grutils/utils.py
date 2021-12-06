#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

from .error import Error


def strip_if_str(s):
    if type(s) == str:
        return s.strip()
    else:
        return s


def to_float(v):
    try:
        f = float(v)
        return True, f
    except Exception as e:
        return False, 'can not parse number from value: {}, error: {}'.format(v, e)


def to_int(v):
    is_float, result = to_float(v)
    if is_float:
        return True, int(round(result))

    return False, result


def int_value_of(v, err: Error, default_i=None):
    ok, result = to_int(v)
    if ok:
        return result
    else:
        err.append(result)
        return default_i


def parse_as_str_if_float_or_int(v):
    if type(v) == float:
        i = int(round(v, 0))
        return '{}'.format(i)
    elif type(v) == int:
        return '{}'.format(v)
    else:
        return v


def is_none_or_empty(s: str):
    return (type(s) == str and len(s) == 0) or (s is None)


def date_of(a: any):
    t = type(a)
    if t == str:
        return date.fromisoformat(a)  # format: "2021-01-03"
    elif t == datetime:
        return a.date()
    elif t == date:
        return a
    else:
        s = 'cannot parse date from ({})'.format(a)
        raise Exception(s)


def field_of(d: Dict[any, any], key: any):
    return None if d is None else (d[key] if key in d else None)


def float_02(f: float):
    return round(f * 100) / 100


def sort_and_merge_ints(ints: List[int]):
    results: List[Tuple[int, int]] = []
    if len(ints) == 0:
        return results

    sorted_ints = sorted(ints)

    start: Optional[int] = None
    curr: Optional[int] = None
    for i in sorted_ints:
        if start is None:
            start = i
            curr = i
            continue

        if i == curr + 1:
            curr = i
            continue

        results.append((start, curr))
        start = i
        curr = i

    if start is not None:
        results.append((start, curr))

    return results


def get_simple_desc_of_int_groups(groups: List[Tuple[int, int]],
                                  formatter: str = "{}",
                                  linker: str = "-",
                                  joiner: str = ","
                                  ):
    items = list(map(lambda group: (formatter + linker + formatter).format(group[0], group[1]) if group[0] != group[
        1] else formatter.format(group[0]), groups))
    return joiner.join(items)
