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

"""This module starts a preprocessing script, if it exists."""
import importlib.util
import logging
import traceback

from hifis_surveyval.core.settings import Settings
from hifis_surveyval.data_container import DataContainer


class Preprocessor(object):
    """Provides running a preprocessing script."""

    @classmethod
    def preprocess(
        cls, settings: Settings, data: DataContainer
    ) -> DataContainer:
        """
        Run preprocessing script.

        Exceptions raised from import will be caught and logged as error on
        the console.

        Args:
            settings (Settings): The settings of the run.
            data (DataContainer): The data to preprocess.

        Raises:
            ImportError: Exception thrown if script could not be loaded.
            AttributeError: Exception thrown if run method could not be
            executed.
        """
        if not settings.PREPROCESSING_FILENAME.exists():
            logging.info(
                "No preprocessing script found - skipping preprocessing"
            )
            return data

        logging.info("Running preprocessing script.")

        module_name = settings.PREPROCESSING_FILENAME.stem

        try:
            spec = importlib.util.spec_from_file_location(
                module_name, settings.PREPROCESSING_FILENAME
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except ImportError as error:
            logging.error(f"Failed to load module {module_name}." f"{error}")

        try:
            preprocessed_data: DataContainer = module.preprocess(data=data)
            return preprocessed_data
        except AttributeError as error:
            traceback.print_exc()
            logging.error(
                f"Module {module_name}: "
                f"Error when calling preprocess() - method: "
                f"{error}."
            )
            return data
