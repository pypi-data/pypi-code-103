# -*- coding: utf-8 -*-
# @File    : func.py
# @Time    : 2021/11/26 4:45 下午

from typing import Any


def integer(s: Any, default: int = 0) -> int:
    """
    Format to an integer
    """
    try:
        return int(s)
    except (TypeError, ValueError):
        return default


def replace_slots(s: str, **slots) -> str:
    """
    Replace the template slot
    """
    for name, value in slots.items():
        s = s.replace("${%s}" % name, str(value))
    return s
