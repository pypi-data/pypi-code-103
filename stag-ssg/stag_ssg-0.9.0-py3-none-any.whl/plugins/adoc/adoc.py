# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import asyncio
from asyncio.subprocess import PIPE
import os
import logging

import attr

from stag.ecs import Page, Content, Metadata
from stag.plugins._helpers import read_file

log = logging.getLogger(__name__)


ADOC_EXTENSIONS = {"adoc", "asc", "asciidoc"}


def get_process_limit():
    count = os.cpu_count()
    if count is None:
        return 2
    return count


@attr.s(auto_attribs=True)
class AsciidocConfig:
    process_limit: int = get_process_limit()


def is_adoc(page):
    return page.source and page.source.ext in ADOC_EXTENSIONS


def is_opened_md(page):
    return page.input and page.input.type == "asciidoc"


def deduce_url(path):
    if path.filebase == "index":
        return path.reldirname
    return os.path.join(path.reldirname, path.filebase)


async def asciidoctor(content):
    proc = await asyncio.create_subprocess_exec(
        "asciidoctor",
        "--no-header-footer",
        "--out-file",
        "-",
        "-",
        stdout=PIPE,
        stdin=PIPE,
    )
    stdout, _ = await proc.communicate(content.encode())
    html = stdout.decode()
    return html


async def generate_page(page):
    if not "title" in page.metadata:
        log.error(f"No title in {page.source.relpath}")
        return

    html = await asciidoctor(page.input.content)
    page.output = Content("html", html)


def chunks(iterable, size):
    if size == 0:
        yield iterable
        return

    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


async def generate_async(site):
    myconfig = site.config.plugins.asciidoc

    adocs = []
    for page in site.pages:
        if not is_opened_md(page):
            continue
        adocs.append(generate_page(page))

    for chunk in chunks(adocs, myconfig.process_limit):
        await asyncio.gather(*chunk)


def read(page):
    if not is_adoc(page):
        return

    metadata, content, _ = read_file(page.source.path)
    page.metadata = Metadata(metadata)
    page.input = Content("asciidoc", content)


def generate(site):
    asyncio.run(generate_async(site))


def register_plugin(site):
    site.config.update_plugin_table("asciidoc", AsciidocConfig())
    site.signals.page_added.connect(read)
    site.signals.processors_init.connect(generate)
    site.readers.register_reader(deduce_url, lambda p: p.ext in ADOC_EXTENSIONS)
