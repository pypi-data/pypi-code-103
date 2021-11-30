# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxrun.exceptions import InvalidArgument


def subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in subclasses(c)]
    )


class Device:
    name = ""

    @classmethod
    def select(cls, name):
        for subclass in subclasses(cls):

            if subclass.name == name:
                return subclass
        raise InvalidArgument(f"Unknown device {name}")

    @classmethod
    def list(cls):
        return sorted([s.name for s in subclasses(cls) if s.name])

    def validate(self, **kwargs):
        raise NotImplementedError()  # pragma: no cover

    def definition(self, **kwargs):
        raise NotImplementedError()  # pragma: no cover

    def device_dict(self, context):
        raise NotImplementedError()  # pragma: no cover


import tuxrun.devices.fvp  # noqa: E402
import tuxrun.devices.qemu  # noqa: E402,F401
