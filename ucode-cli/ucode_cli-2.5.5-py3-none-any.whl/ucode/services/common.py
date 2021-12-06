# coding=utf-8
import logging

__author__ = 'ThucNC'

import re

_logger = logging.getLogger(__name__)


def find_section(pattern, lines, start_index=0, once=False, until_pattern="^#", skip_section_header=True):
    """
    Find a section in list of lines of text, start with line match `pattern`,
    until the next line that matches `until_pattern`
    @param skip_section_header:
    @param until_pattern:
    @param pattern:
    @param lines:
    @param start_index:
    @param once:
    @return: list of starting indices for each section found, and dict of their content
    """
    indices = []
    content = {}
    for i in range(start_index, len(lines)):
        if re.match(pattern, lines[i], re.I):
            indices.append(i)
            content.setdefault(i, [])
            if not skip_section_header:
                content[i].append(lines[i])
            for j in range(i+1, len(lines)):
                if re.match(until_pattern, lines[j], re.I):
                    break
                content[i].append(lines[j])
            if once:
                break

    return indices, content
