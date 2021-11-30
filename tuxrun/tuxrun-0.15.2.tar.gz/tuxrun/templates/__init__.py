# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from functools import cache
from pathlib import Path

import jinja2


BASE = (Path(__file__) / "..").resolve()


@cache
def jobs():
    return jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        loader=jinja2.FileSystemLoader(str(BASE / "jobs")),
        undefined=jinja2.StrictUndefined,
    )


@cache
def devices():
    return jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        loader=jinja2.FileSystemLoader(str(BASE / "devices")),
    )


@cache
def dispatchers():
    return jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        loader=jinja2.FileSystemLoader(str(BASE / "dispatchers")),
    )


@cache
def tests():
    return jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        loader=jinja2.FileSystemLoader(str(BASE / "tests")),
    )


@cache
def wrappers():
    return jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        loader=jinja2.FileSystemLoader(str(BASE / "wrappers")),
    )
