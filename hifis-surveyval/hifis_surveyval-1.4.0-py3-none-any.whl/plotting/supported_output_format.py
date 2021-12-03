# hifis-surveyval
# Framework to help developing analysis scripts for the HIFIS Software survey.
#
# SPDX-FileCopyrightText: 2021 HIFIS Software <support@hifis.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
This module provides a way of handling output formats for plotters.

.. currentmodule:: hifis_surveyval.plotting.supported_output_format
.. moduleauthor:: HIFIS Software <software@hifis.net>
"""
from enum import Enum, auto, unique
from typing import Set


@unique
class SupportedOutputFormat(Enum):
    """An abstraction of the supported output formats for generated images."""

    SCREEN = auto()
    PDF = auto()
    PNG = auto()
    SVG = auto()

    def __str__(self) -> str:
        """
        Get a string representation of a supported output format.

        Returns:
            str: String representation of a supported output format.
        """
        return self.name

    @classmethod
    def list(cls) -> Set:
        """
        Generate a set listing the supported output formats.

        Returns:
            Set: Set of supported output formats.
        """
        return set(value.name for value in SupportedOutputFormat)

    @classmethod
    def from_str(cls, enum_entry: str) -> Enum:
        """
        Generate an enum object from a string.

        Args:
            enum_entry (str): String to be converted into another string
                              representing a supported output format.

        Returns:
            Enum: Enumeration entry that has been selected.

        Raises:
            NotImplementedError: Exception thrown if output format is not
                                 supported.
        """
        output_format: SupportedOutputFormat
        for output_format in SupportedOutputFormat:
            if output_format.name == enum_entry:
                return output_format
        raise NotImplementedError(
            f"{enum_entry} is currently not implemented."
            f"Only {SupportedOutputFormat.list()} may be chosen."
        )
