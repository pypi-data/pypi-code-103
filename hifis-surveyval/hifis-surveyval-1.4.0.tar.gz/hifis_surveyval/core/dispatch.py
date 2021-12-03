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

"""This module allows discovery and dispatch of analysis functions."""
import copy
import importlib.util
import logging
import traceback
from pathlib import Path
from typing import List

from hifis_surveyval.data_container import DataContainer
from hifis_surveyval.hifis_surveyval import HIFISSurveyval


class Dispatcher(object):
    """
    Provides analysis function module and execution facilities.

    The operations are based on a module folder and optionally a list of
    module names to be given at initialization.
    """

    def __init__(self, surveyval: HIFISSurveyval, data: DataContainer) -> None:
        """
        Initialize the Dispatcher.

        Args:
            surveyval (HIFISSurveyval): Passing HIFISSurveyval object in in
                                        order to pass it through to
                                        particular analysis scripts.
        """
        self.surveyval: HIFISSurveyval = surveyval
        self.data: DataContainer = data
        self.module_folder: Path = self.surveyval.settings.SCRIPT_FOLDER
        self.module_names: List[str] = self.surveyval.settings.SCRIPT_NAMES
        self.module_name_paths: List[Path] = []
        self._discovered_modules: List[str] = []

        self.__validate_config()

    def __validate_config(self) -> None:
        """
        Check if paths and modules exist.

        Raises:
            ValueError: Exception thrown if script folder does not exist.
            ValueError: Exception thrown if script folder is not a directory.
            ValueError: Exception thrown if script is not found.
        """
        if not self.module_folder.exists():
            raise ValueError("Module folder should exist.")
        if not self.module_folder.is_dir():
            raise ValueError("Module folder should be a directory.")

        # Check that all selected modules exist in module folder.
        if self.module_names:
            for module_name in self.module_names:
                module_path: Path = Path(
                    self.module_folder, f"{module_name}.py"
                )
                if not module_path.exists():
                    raise ValueError(
                        f"Module {module_name} not found in " f"module folder."
                    )
                self.module_name_paths.append(module_path)
        else:
            self.module_name_paths.extend(self.module_folder.iterdir())

    def discover(self) -> None:
        """
        Discover all potential or selected modules in the module folder.

        Iterate over all modules in the module folder (non-recursive) or
        selected modules only and cache the names of those python (.py) files.
        Exception: __init__.py is excluded.
        """
        # Execute all scripts in scripts folder or selected scripts only.
        for name_path in self.module_name_paths:
            if (
                name_path.is_file()
                and name_path.suffix == ".py"
                and not name_path.stem == "__init__"
            ):
                logging.info(f"Discovered module {name_path.stem}.")
                self._discovered_modules.append(name_path.stem)

    def load_all_modules(self) -> None:
        """
        Try to load and run all discovered modules.

        Make sure to run discover() beforehand.
        If no modules have been discovered, a warning will be logged.
        See Also: load_module()

        """
        if not self._discovered_modules:
            logging.warning("No modules have been discovered - Nothing to do.")
            return

        for module_name in self._discovered_modules:
            self.load_module(module_name)

    def load_module(self, module_name: str) -> None:
        """
        Attempt to load a module given by name.

        Exceptions raised from import will be caught and logged as error on
        the console.

        Args:
            module_name (str): The name of the module, without the .py ending

        Raises:
            ImportError: Exception thrown if script could not be loaded.
            AttributeError: Exception thrown if run method could not be
            executed.
        """
        # TODO if the module_name has a .py ending, remove it beforehand

        module_path: Path = self.module_folder / module_name
        logging.info(f"Running Module {module_name}.")

        try:
            spec = importlib.util.spec_from_file_location(
                module_name, f"{module_path}.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except ImportError as error:
            logging.error(f"Failed to load module {module_name}." f"{error}")

        try:
            module.run(
                hifis_surveyval=copy.deepcopy(self.surveyval),
                data=copy.deepcopy(self.data),
            )
        except AttributeError as error:
            traceback.print_exc()
            logging.error(
                f"Module {module_name}: "
                f"Error when calling run() - method: "
                f"{error}."
            )
