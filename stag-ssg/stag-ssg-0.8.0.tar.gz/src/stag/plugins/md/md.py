# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import os
import itertools

from typing import List

import attr
import markdown

from stag.ecs import Page, Content, Metadata
from stag.plugins._helpers import read_file


def is_md(page):
    return page.source and page.source.ext == "md"


def is_opened_md(page):
    return page.input and page.input.type == "md"


@attr.s(auto_attribs=True)
class MarkdownConfig:
    extensions: List[str] = attr.Factory(lambda: ["footnotes", "fenced_code", "smarty"])


def deduce_url(path):
    if path.filebase == "index":
        return path.reldirname
    return os.path.join(path.reldirname, path.filebase)


def read(page):
    if not is_md(page):
        return

    metadata, content, _ = read_file(page.source.path)
    page.metadata = Metadata(metadata)
    page.input = Content("md", content)


def generate(site):
    myconfig = site.config.plugins.markdown
    conv = markdown.Markdown(extensions=myconfig.extensions)

    for page in site.pages:
        if not is_opened_md(page):
            continue

        assert "title" in page.metadata, f"No title in {page.source.relpath}"
        html = conv.reset().convert(page.input.content)
        page.output = Content("html", html)


def register_plugin(site):
    site.config.update_plugin_table("markdown", MarkdownConfig())
    site.signals.page_added.connect(read)
    site.signals.processors_init.connect(generate)
    site.readers.register_reader(deduce_url, lambda p: p.ext == "md")
