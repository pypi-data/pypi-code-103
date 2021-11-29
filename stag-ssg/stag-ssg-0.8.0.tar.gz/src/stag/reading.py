# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import attr

from typing import Optional, Callable, List

from stag.ecs import Path


@attr.s(auto_attribs=True)
class ContentReader:
    reader: Callable[[Path], str]
    condition: Optional[Callable[[Path], bool]] = None


@attr.s(auto_attribs=True)
class Readers:
    _readers: List[ContentReader] = attr.ib(factory=list)

    def register_reader(self, reader, condition=None):
        self._readers.append(ContentReader(reader, condition))

    def get_path(self, path):
        reader = next(
            (r.reader for r in self._readers if r.condition(path)), self._default_path
        )
        return reader(path)

    def _default_path(self, path):
        return path.relpath
