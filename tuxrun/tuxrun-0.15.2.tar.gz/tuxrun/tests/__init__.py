# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import fnmatch

from tuxrun import templates
from tuxrun.exceptions import InvalidArgument


def subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in subclasses(c)]
    )


class Test:
    device: str = ""
    name: str = ""
    timeout: int = 0

    def __init__(self, timeout):
        if timeout:
            self.timeout = timeout

    @classmethod
    def select(cls, name):
        for subclass in subclasses(cls):

            if subclass.name == name:
                return subclass
        raise InvalidArgument(f"Unknown test {name}")

    @classmethod
    def list(cls):
        return sorted([s.name for s in subclasses(cls) if s.name])

    def validate(self, device=device, **kwargs):
        if not fnmatch.fnmatch(device.name, self.device):
            raise InvalidArgument(
                f"Test '{self.name}' not supported on device '{device.name}'"
            )

    def _render(self, filename, **kwargs):
        return templates.tests().get_template(filename).render(**kwargs)


import tuxrun.tests.command  # noqa: E402
import tuxrun.tests.kunit  # noqa: E402
import tuxrun.tests.ltp  # noqa: E402
import tuxrun.tests.morello  # noqa: E402,F401
