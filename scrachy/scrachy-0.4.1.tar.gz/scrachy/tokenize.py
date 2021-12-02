#  Copyright 2020 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.

# Python Modules
from typing import List

# 3rd Party Modules

try:
    import blingfire
except ImportError:
    blingfire = None

# Project Modules


def space_tokenizer(txt: str) -> List[str]:
    """
    Tokenize a string by splitting on whitespace.

    :param txt: The text to tokenize.
    :return: A list of tokens.
    """
    return txt.split()


def character_tokenizer(txt: str) -> List[str]:
    """
    Split a string on each character.

    :param txt: The text to tokenize.
    :return: The list of characters.
    """
    return list(txt)


def blingfire_tokenizer(txt: str) -> List[str]:
    """
    Split a string using the default `BlingFire <https://github.com/microsoft/BlingFire>`_ word
    tokenizer.

    :param txt: The text to tokenize.
    :return: The list of tokens.
    """
    return space_tokenizer(blingfire.text_to_words(txt))
