#!/usr/bin/env python3


# Salut à Toi: an XMPP client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" regex tools common to backend and frontends """

import re
import unicodedata

path_escape = {"%": "%25", "/": "%2F", "\\": "%5c"}
path_escape_rev = {re.escape(v): k for k, v in path_escape.items()}
path_escape = {re.escape(k): v for k, v in path_escape.items()}
#  thanks to Martijn Pieters (https://stackoverflow.com/a/14693789)
RE_ANSI_REMOVE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
RE_TEXT_URL = re.compile(r'[^a-zA-Z0-9,_]+')
TEXT_MAX_LEN = 60
# min lenght is currently deactivated
TEXT_WORD_MIN_LENGHT = 0


def reJoin(exps):
    """Join (OR) various regexes"""
    return re.compile("|".join(exps))


def reSubDict(pattern, repl_dict, string):
    """Replace key, value found in dict according to pattern

    @param pattern(basestr): pattern using keys found in repl_dict
    @repl_dict(dict): keys found in this dict will be replaced by
        corresponding values
    @param string(basestr): string to use for the replacement
    """
    return pattern.sub(lambda m: repl_dict[re.escape(m.group(0))], string)


path_escape_re = reJoin(list(path_escape.keys()))
path_escape_rev_re = reJoin(list(path_escape_rev.keys()))


def pathEscape(string):
    """Escape string so it can be use in a file path

    @param string(basestr): string to escape
    @return (str, unicode): escaped string, usable in a file path
    """
    return reSubDict(path_escape_re, path_escape, string)


def pathUnescape(string):
    """Unescape string from value found in file path

    @param string(basestr): string found in file path
    @return (str, unicode): unescaped string
    """
    return reSubDict(path_escape_rev_re, path_escape_rev, string)


def ansiRemove(string):
    """Remove ANSI escape codes from string

    @param string(basestr): string to filter
    @return (str, unicode): string without ANSI escape codes
    """
    return RE_ANSI_REMOVE.sub("", string)


def urlFriendlyText(text):
    """Convert text to url-friendly one"""
    # we change special chars to ascii one,
    # trick found at https://stackoverflow.com/a/3194567
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    text = RE_TEXT_URL.sub(' ', text).lower()
    text = '-'.join([t for t in text.split() if t and len(t)>=TEXT_WORD_MIN_LENGHT])
    while len(text) > TEXT_MAX_LEN:
        if '-' in text:
            text = text.rsplit('-', 1)[0]
        else:
            text = text[:TEXT_MAX_LEN]
    return text
