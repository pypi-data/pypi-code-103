# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import os
from fnmatch import fnmatch
from urllib.parse import urljoin

from typing import Optional as _Optional
from collections.abc import Mapping as _Mapping

import attr

from stag.ecs import Page
from stag.signals import signal, Signals
from stag.reading import Readers


# sentinel used for parameters for which None is a valid value
_ANY = "_ANY"


def _urlize(url):
    url = url.strip("/")
    return f"/{url}"


def _absurl(base, path):
    return urljoin(base, path)


@attr.s(auto_attribs=True)
class Site:
    config: dict = attr.ib(repr=False)
    _pages: _Mapping[str, Page] = attr.ib(factory=dict, repr=False)
    _signals: Signals = attr.ib(init=False, factory=Signals, repr=False)
    _readers: Readers = attr.ib(init=False, factory=Readers, repr=False)

    @property
    def signals(self):
        return self._signals

    @property
    def readers(self):
        return self._readers

    @property
    def pages(self):
        return list(self._pages.values())

    @property
    def taxonomies(self):
        for page in self.pages:
            if page.taxonomy:
                yield page

    @property
    def ordinary_pages(self):
        for page in self._pages.values():
            if page.source and page.input and page.output and page.metadata:
                yield page

    def subpages_of(self, val, recursive=False):
        def _cmp(pardir, exp):
            return pardir == exp

        def _cmp_r(pardir, exp):
            cp = os.path.commonpath([pardir, exp])
            return cp == exp

        cmp_fn = _cmp_r if recursive else _cmp

        base = _urlize(val)
        for page in self.ordinary_pages:
            pardir = os.path.dirname(page.relurl)
            if cmp_fn(pardir, base):
                yield page

    def make_page(self, path, **kw):
        path = _urlize(path)
        if path in self._pages:
            raise ValueError(f"URL {path} already exists")

        url = _absurl(self.config.url, path)
        page = Page(url, **kw)
        self._pages[path] = page
        self.signals.page_added.emit(page)
        return page

    def get_or_make_page(self, path, **kw):
        path = _urlize(path)
        if path in self._pages:
            return self._pages[path]

        url = _absurl(self.config.url, path)
        page = Page(url, **kw)
        self._pages[path] = page
        self.signals.page_added.emit(page)
        return page

    def filter_pages(self, ptype=_ANY):
        for page in self.pages:
            if page.metadata is not None and ptype is _ANY:
                yield page
            elif page.metadata is not None and page.metadata.get("type", _ANY) == ptype:
                yield page

    def find(self, path):
        return self._pages.get(_urlize(path))

    def resources(self, page, basename_glob=None):
        for other in self.pages:
            if (
                other != page
                and other.source
                and page.source
                and other.source.reldirname == page.source.reldirname
            ) and (
                basename_glob is None or fnmatch(other.source.basename, basename_glob)
            ):
                yield other


@attr.s(auto_attribs=True)
class SiteTemplateProxy:
    _site: Site

    def __getattr__(self, name):
        forbidden = {"signals", "readers", "make_page", "get_or_make_page"}
        if name in forbidden:
            raise AttributeError(f"Access to {name} is forbidden from inside template")
        return getattr(self._site, name)
