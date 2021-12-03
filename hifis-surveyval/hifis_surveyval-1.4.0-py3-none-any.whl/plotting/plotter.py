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
This module provides a framework for plotters.

.. currentmodule:: hifis_surveyval.plotting.plotter
.. moduleauthor:: HIFIS Software <software@hifis.net>
"""

from abc import ABC
from pathlib import Path

from hifis_surveyval.plotting.supported_output_format import \
    SupportedOutputFormat


class Plotter(ABC):
    """Base class to derive plotters from."""

    def __init__(
        self, output_format: SupportedOutputFormat, output_path: Path
    ) -> None:
        """
        Initialize a plotter.

        Args:
            output_format (SupportedOutputFormat): Supported output format.
            output_path (Path): Path to the output folder.
        """
        self.OUTPUT_FORMAT: SupportedOutputFormat = output_format
        self.ANALYSIS_OUTPUT_PATH: Path = output_path
