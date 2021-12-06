# coding=utf-8
import base64
import fnmatch
import glob
import logging

__author__ = 'ThucNC'

import os

import re

from unidecode import unidecode

_logger = logging.getLogger(__name__)


def join_lines(lines):
    return ''.join([l+'\n' for l in lines]).strip()


def make_slug(s):
    s = unidecode(s).lower()
    # print("unidecode: ", s)
    s2 = ""
    for c in s:
        if c.isalnum():
            s2 += c
        else:
            s2 += " "

    return "-".join(s2.split())


def make_problem_code(name):
    name = make_slug(name)
    name = name.strip(" _").replace("-", "_")
    if not name:
        return name
    if '0' <= name[0] <= '9':
        name = "p" + name
    return name


def base64_encode(data: str) -> str:
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')


def base64_decode(data: str) -> str:
    return base64.b64decode(data.encode('utf-8')).decode('utf-8')


def findfiles(pattern, folder='.'):
    """
    Returns list of filenames from `where` path matched by 'which'
    shell pattern. Matching is case-insensitive.
    """

    # TODO: recursive param with walk() filtering
    rule = re.compile(fnmatch.translate(pattern), re.IGNORECASE)
    return [os.path.join(folder, name) for name in os.listdir(folder) if rule.match(name)]


def dos2unix(s):
    return s.replace('\r\n', '\n')