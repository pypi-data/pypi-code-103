#!/usr/bin/env python3

# Libervia: an XMPP client
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

"""Misc utils for both backend and frontends"""

import collections.abc
size_units = {
    "b": 1,
    "kb": 1000,
    "mb": 1000**2,
    "gb": 1000**3,
    "tb": 1000**4,
    "pb": 1000**5,
    "eb": 1000**6,
    "zb": 1000**7,
    "yb": 1000**8,
    "o": 1,
    "ko": 1000,
    "mo": 1000**2,
    "go": 1000**3,
    "to": 1000**4,
    "po": 1000**5,
    "eo": 1000**6,
    "zo": 1000**7,
    "yo": 1000**8,
    "kib": 1024,
    "mib": 1024**2,
    "gib": 1024**3,
    "tib": 1024**4,
    "pib": 1024**5,
    "eib": 1024**6,
    "zib": 1024**7,
    "yib": 1024**8,
    "kio": 1024,
    "mio": 1024**2,
    "gio": 1024**3,
    "tio": 1024**4,
    "pio": 1024**5,
    "eio": 1024**6,
    "zio": 1024**7,
    "yio": 1024**8,
}


def per_luminance(red, green, blue):
    """Caculate the perceived luminance of a RGB color

    @param red(int): 0-1 normalized value of red
    @param green(int): 0-1 normalized value of green
    @param blue(int): 0-1 normalized value of blue
    @return (float): 0-1 value of luminance (<0.5 is dark, else it's light)
    """
    # cf. https://stackoverflow.com/a/1855903, thanks Gacek

    return 0.299 * red + 0.587 * green + 0.114 * blue


def recursive_update(ori: dict, update: dict):
    """Recursively update a dictionary"""
    # cf. https://stackoverflow.com/a/3233356, thanks Alex Martelli
    for k, v in update.items():
        if isinstance(v, collections.abc.Mapping):
            ori[k] = recursive_update(ori.get(k, {}), v)
        else:
            ori[k] = v
    return ori

class OrderedSet(collections.abc.MutableSet):
    """A mutable sequence which doesn't keep duplicates"""
    # TODO: complete missing set methods

    def __init__(self, values=None):
        self._dict = {}
        if values is not None:
            self.update(values)

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict.keys())

    def __contains__(self, item):
        return item in self._dict

    def add(self, item):
        self._dict[item] = None

    def discard(self, item):
        try:
            del self._dict[item]
        except KeyError:
            pass

    def update(self, items):
        self._dict.update({i: None for i in items})


def parseSize(size):
    """Parse a file size with optional multiple symbole"""
    try:
        return int(size)
    except ValueError:
        number = []
        symbol = []
        try:
            for c in size:
                if c == " ":
                    continue
                if c.isdigit():
                    number.append(c)
                elif c.isalpha():
                    symbol.append(c)
                else:
                    raise ValueError("unexpected char in size: {c!r} (size: {size!r})")
            number = int("".join(number))
            symbol = "".join(symbol)
            if symbol:
                try:
                    multiplier = size_units[symbol.lower()]
                except KeyError:
                    raise ValueError(
                        "unknown size multiplier symbole: {symbol!r} (size: {size!r})")
                else:
                    return number * multiplier
            return number
        except Exception as e:
            raise ValueError(f"invalid size: {e}")


def getSizeMultiplier(size, suffix="o"):
    """Get multiplier of a file size"""
    size = int(size)
    #  cf. https://stackoverflow.com/a/1094933 (thanks)
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(size) < 1024.0:
            return size, f"{unit}{suffix}"
        size /= 1024.0
    return size, f"Yi{suffix}"


def getHumanSize(size, suffix="o", sep=" "):
    size, symbol = getSizeMultiplier(size, suffix)
    return f"{size:.2f}{sep}{symbol}"
