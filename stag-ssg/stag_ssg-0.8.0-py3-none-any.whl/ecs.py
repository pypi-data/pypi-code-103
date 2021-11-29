# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

from __future__ import annotations

import os
from collections import UserDict, defaultdict
from datetime import date as _date_t
from datetime import datetime as _datetime_t
from urllib.parse import urlparse
from functools import cache

from typing import Optional as _Optional
from typing import List as _List
from typing import Set as _Set
from typing import Any as _Any

import attr
from dateutil.parser import parse as _parse_dt

from stag.signals import signal


@attr.s(auto_attribs=True, frozen=True)
class Path:
    path: str
    root_dir: str

    @property
    def relpath(self):
        return self.path[len(self.root_dir) :].strip("/")

    @property
    def ext(self):
        return os.path.splitext(self.path)[1][len(os.extsep) :]

    @property
    def filebase(self):
        return os.path.splitext(self.basename)[0]

    @property
    def basename(self):
        return os.path.basename(self.path)

    @property
    def reldirname(self):
        return os.path.dirname(self.relpath)


@attr.s(auto_attribs=True)
class Content:
    type: str
    content: _Any = attr.ib(None, repr=False)


class Metadata(UserDict):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._normalize_data()

    def _normalize_data(self):
        title = self.data.get("title", "")

        # date and lastmod can be used exclusively:
        # - if both are set, they are used directly
        # - if date is set and lastmod is unset, lastmod=date
        # - if date is unset and lastmod is set, date=lastmod
        # - if both are unset, lastmod=date=None
        date = self.data.get("date", self.data.get("lastmod"))
        if date:
            if isinstance(date, (int, str, float)):
                self.data["date"] = _parse_dt(date)
            elif type(date) == _date_t:
                self.data["date"] = _datetime_t.fromordinal(date.toordinal())
            self.data["timestamp"] = self.data["date"].timestamp()

        lastmod = self.data.get("lastmod")
        if lastmod:
            if isinstance(lastmod, (int, str, float)):
                self.data["lastmod"] = _parse_dt(lastmod)
            elif type(lastmod) == _date_t:
                self.data["lastmod"] = _datetime_t.fromordinal(lastmod.toordinal())
            self.data["lastmod_timestamp"] = self.data["lastmod"].timestamp()
        else:
            lastmod = self.data.get("date")
            if lastmod:
                self.data["lastmod"] = lastmod
                self.data["lastmod_timestamp"] = lastmod.timestamp()

        self.__dict__.update(self.data)


@attr.s(auto_attribs=True)
class Taxonomy:
    name: str
    singular: str
    plural: str
    terms: _List[Page] = attr.ib(factory=list, repr=False)
    possible_terms: _Optional[_Set[str]] = attr.ib(None, repr=False)


@attr.s(auto_attribs=True)
class Term:
    name: str
    pages: _List[Page] = attr.ib(factory=list)


class _Notified:
    """Descriptor of fields which should automatically notify some of their
    changes."""

    def __init__(self, name):
        self.name = name
        self.real = "_" + name

    def __get__(self, obj, objtype):
        return getattr(obj, self.real)

    def __set__(self, obj, val):
        curr = getattr(obj, self.real)
        setattr(obj, self.real, val)

        # emit signals
        if val is None and curr is not None:
            signame = f"{self.name}_removed"
            getattr(obj, signame).emit(obj, curr)
        elif val != curr:
            signame = f"{self.name}_created"
            getattr(obj, signame).emit(obj, val)


def component(type_, **kw):
    kw.setdefault("metadata", {})["component"] = True
    kw.setdefault("repr", False)
    return attr.ib(None, **kw)


def component_descriptors(cls):
    for a in cls.__attrs_attrs__:
        if a.metadata and a.metadata.get("component"):
            dname = a.name.lstrip("_")
            setattr(cls, dname, _Notified(dname))

    return cls


@component_descriptors
@attr.s(auto_attribs=True, cmp=False, hash=False)
class Page:
    _url: str = attr.ib(converter=urlparse)

    _metadata: _Optional[Metadata] = component(Metadata)
    _source: _Optional[Path] = component(Path)
    _input: _Optional[Content] = component(Content)
    _output: _Optional[Content] = component(Content)
    _taxonomy: _Optional[Taxonomy] = component(Taxonomy)
    _term: _Optional[Term] = component(Term)

    def __attrs_post_init__(self):
        for a in self.__attrs_attrs__:
            dname = a.name.lstrip("_")
            if a.metadata and a.metadata.get("component"):
                crsig = f"{dname}_created"
                setattr(self, crsig, signal(crsig))
                rmsig = f"{dname}_removed"
                setattr(self, rmsig, signal(rmsig))

    @property
    @cache
    def url(self):
        return self._url.geturl()

    @property
    @cache
    def relurl(self):
        return self._url.path

    @property
    def md(self):
        return self._metadata

    def __hash__(self):
        return hash(self._url)

    def __eq__(self, other):
        return self._url == other._url

    def __lt__(self, other):
        return self._url < other._url
