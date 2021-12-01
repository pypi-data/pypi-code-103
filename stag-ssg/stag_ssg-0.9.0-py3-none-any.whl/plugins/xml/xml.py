# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import os
from datetime import datetime

import tomli

from stag.ecs import Page, Content, Metadata
from stag.plugins._helpers import read_file


def is_xml(page):
    return page.source and page.source.ext == "xml"


def read(page):
    if not is_xml(page):
        return

    md, cn, _ = read_file(page.source.path)
    md.setdefault("title", page.source.filebase.capitalize())
    md.setdefault("type", page.source.filebase)
    md.setdefault("date", datetime.now())
    page.metadata = Metadata(md)
    page.input = Content("xml", cn)
    page.output = Content("xml", cn)


def register_plugin(site):
    site.signals.page_added.connect(read)
