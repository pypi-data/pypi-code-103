# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import os
from collections import UserDict, UserList
from contextlib import contextmanager as _contextmanager
from datetime import date as _date_t
from datetime import datetime as _datetime_t


@_contextmanager
def chdir(path):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


class SortDate:
    def __init__(self, page, key="timestamp"):
        self.ts = page.metadata.get(key) if page.metadata else None

    def __lt__(self, other):
        if self.ts and other.ts:
            return self.ts < other.ts
        return self.ts and not other.ts


def date_sorting_key(key="timestamp"):
    def factory(*a, **kw):
        kw["key"] = key
        return SortDate(*a, **kw)

    return factory


class AttrDict(UserDict):
    def __getitem__(self, key):
        return attr_access(self.data[key])

    def __getattr__(self, key):
        try:
            return attr_access(getattr(self.data, key))
        except AttributeError:
            try:
                return self[key]
            except KeyError:
                raise AttributeError(key)


class AttrList(UserList):
    def __getitem__(self, key):
        return attr_access(self.data[key])


def attr_access(val):
    if isinstance(val, dict):
        return AttrDict(val)
    if isinstance(val, (tuple, list)):
        return AttrList(val)
    return val
