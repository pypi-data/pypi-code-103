# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2021 Michał Góral.

import itertools
import logging
import tomli

log = logging.getLogger(__name__)


def read_file(path):
    frontmatter = None
    frontmatter_parsed = False

    metadata = []
    content = []

    step = None  # forward declaration

    def detect_frontmatter(line):
        # front matter must be a line consisting of at least 3 the same characters
        return line and len(line) > 2 and all(ch == line[0] for ch in line)

    def parse_content(line):
        nonlocal content
        content.append(line)

    def parse_frontmatter(line):
        nonlocal frontmatter, frontmatter_parsed, metadata, step
        if frontmatter is None:  # possible only on the first line
            if detect_frontmatter(line):
                frontmatter = line
            else:
                step = parse_content
                step(line)
        elif line == frontmatter:
            frontmatter_parsed = True
            step = parse_content
        else:
            metadata.append(line)

    step = parse_frontmatter

    with open(path) as fd:
        for line in fd:
            line = line.rstrip("\r\n")
            step(line)

    if frontmatter and not frontmatter_parsed:
        log.warning(f"{path}: front matter recognised, but not closed.")

    if frontmatter_parsed:
        md = tomli.loads("\n".join(metadata))
        cn = "\n".join(content)
    else:
        md = {}
        if frontmatter is not None:
            cn = "\n".join(itertools.chain([frontmatter], content))
        else:
            cn = "\n".join(content)

    return md, cn, frontmatter_parsed
