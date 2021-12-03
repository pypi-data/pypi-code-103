#!/usr/bin/env python

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

# -*- coding: utf-8 -*-

"""This project is used to develop analysis scripts for surveys."""
import sys

from hifis_surveyval.core.settings import Settings
from hifis_surveyval.plotting.matplotlib_plotter import MatplotlibPlotter
from hifis_surveyval.printing.printer import Printer


class HIFISSurveyval:
    """
    Main class for all functionalities.

    Also serves as data storage.
    """

    def __init__(self, settings: Settings):
        """
        Initialize HIFISSurveyval.

        Args:
              settings:
                A Settings container to store the setup configuration
                in. It will be populated with the related settings during the
                initialization of the HIFISSurveyval object.
        """
        #: The settings storage
        self.settings: Settings = settings

        # register plotter
        self.plotter: MatplotlibPlotter = MatplotlibPlotter(
            output_format=self.settings.OUTPUT_FORMAT,
            output_path=self.settings.ANALYSIS_OUTPUT_PATH,
        )

        # register printer
        self.printer: Printer = Printer()
        self._prepare_environment()

    def _prepare_environment(self) -> None:
        """
        Prepare the runtime environment.

        * setting sys path to load scripts
        * creating output folder to save images
        """
        # set syspath to later on load scripts
        sys.path.insert(0, str(self.settings.SCRIPT_FOLDER.resolve()))

        # create folder to output the results
        if self.settings.ANALYSIS_OUTPUT_PATH is not None:
            if not self.settings.ANALYSIS_OUTPUT_PATH.exists():
                self.settings.ANALYSIS_OUTPUT_PATH.mkdir(parents=True)
