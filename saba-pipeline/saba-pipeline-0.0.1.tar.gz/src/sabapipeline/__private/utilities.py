# from strongtyping.strong_typing import match_typing
from typing import *
from abc import ABC, abstractmethod


def get_not_none(obj: Any, default: Any):
    return default if obj is None else obj