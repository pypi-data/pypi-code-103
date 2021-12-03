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
This module handles settings.

It provides:
* settings classes
* getter for settings
* an export function to create a file
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml
from pydantic import BaseSettings, validator

from hifis_surveyval.plotting.supported_output_format import (
    SupportedOutputFormat,
)


class SystemSettings(BaseSettings):
    """Settings, that are not loaded from file."""

    # Path to config Filename
    CONFIG_FILENAME: Path = Path("hifis-surveyval.yml")

    VERBOSITY: int = logging.NOTSET

    # The date prefix is used to identify the run
    # (e.g. for saving output images)
    RUN_TIMESTAMP: str = None

    @validator("RUN_TIMESTAMP", pre=True)
    def set_timestamp(cls, to_validate: str) -> str:
        """
        Get the current datetime.

        Args:
            to_validate (str): Date-time string to be validated.

        Returns:
            str: Date-time string in a specific format.
        """
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Path to sub-folder which holds all output files of a single
    # analysis run
    ANALYSIS_OUTPUT_PATH: Path = None

    @validator("ANALYSIS_OUTPUT_PATH")
    def assemble_output_path(
        cls, to_validate: str, values: Dict[str, Any]
    ) -> Path:
        """
        Assemble path from user settings and datetime.

        Args:
            to_validate (str):
                Analysis output path as string to be validated.
            values (Dict[str, Any]):
                Parts of the analysis output path to be
                concatenated as an absolute path.
        Returns:
            Path: Path to the output folder of the an analysis run.
        """
        return values.get("OUTPUT_FOLDER") / values.get("RUN_TIMESTAMP")

    # Using a set for true_values and false_values to avoid duplicates and
    # because order does not matter
    TRUE_VALUES: Set[str] = {"True", "Yes", "Y", "On", "1"}
    """
    A set of strings to be interpreted as boolean 'True' when
    parsing the input data.
    """

    FALSE_VALUES: Set[str] = {"False", "No", "N", "Off", "0"}
    """
    A set of strings to be interpreted as boolean 'False' when
    parsing the input data.
    """

    @validator("FALSE_VALUES", "TRUE_VALUES", pre=True)
    def case_insensitive_values(cls, to_validate: Set[str]) -> Set:
        """
        Extend list of values to match all cases.

        Args:
            to_validate (str): Analysis output path as string to be validated.

        Returns:
            Set: Set of false and true values accepted as boolean values in
                 the data.
        """
        additional_lower: Set[str] = set(map(str.lower, to_validate))
        additional_upper: Set[str] = set(map(str.upper, to_validate))
        to_validate.update(additional_lower.union(additional_upper))
        return to_validate


class FileSettings(BaseSettings):
    """Settings, that the user can change."""

    # Path to preprocessing script
    PREPROCESSING_FILENAME: Path = Path("preprocess.py")

    @validator("PREPROCESSING_FILENAME")
    def validate_preprocessing_script(cls, to_validate: Path) -> Path:
        """
        Ensure that preprocessing script is a Python file.

        Args:
            to_validate:
                Preprocessing script path to be validated.
        Returns:
            Path to the preprocessing script.

        Raises:
            ValueError:
                If the given script did not end with ".py" and therefore
                probably is not a python script.
        """
        if to_validate.suffix != ".py":
            raise ValueError("Preprocessing Script must be a python script")

        return to_validate

    # Path to metadata folder
    METADATA: Path = Path("metadata/")

    @validator("METADATA")
    def validate_metadata_folder(cls, to_validate: Path) -> Path:
        """
        Ensure the metadata folder is a folder and exists.

        Args:
            to_validate:
                The path to the metadata folder, which is to be validated.

        Returns:
            The path to the metadata folder if it is valid.

        Raises:
            ValueError:
                If either the given path was not a folder or did not exist.
        """
        if not to_validate.exists():
            raise ValueError(f"Metadata folder {to_validate.absolute()} does "
                             f"not exist")
        if not to_validate.is_dir():
            raise ValueError(f"Metadata folder {to_validate.absolute()} is "
                             f"not a folder")
        return to_validate

    # Path in which modules to be executed are located which defaults
    # to "scripts" folder.
    SCRIPT_FOLDER: Path = Path("scripts")

    # List of selected module names to be executed which defaults to
    # an empty list for all modules in the module folder.
    SCRIPT_NAMES: List[str] = []

    # The Format in which the data should be output
    OUTPUT_FORMAT: SupportedOutputFormat = SupportedOutputFormat.SCREEN

    # Folder, into which the output file goes
    # if the output format is not screen
    OUTPUT_FOLDER: Path = Path("output")

    # The key that is used by LimeSurvey to identify the participants' ID
    # column
    ID_COLUMN_NAME: str = "id"

    # The ID that the framework injects for questions that are named as a
    # question collection by LimeSurvey
    ANONYMOUS_QUESTION_ID: str = "_"

    # Separator used to distinguish the elements in the hierarchical IDs of
    # model elements.
    HIERARCHY_SEPARATOR: str = "/"

    # Separator used in header of CSV data to separate QuestionCollection ID
    # and Question ID.
    DATA_ID_SEPARATOR: str = "_"

    class Config:
        """
        Subclass for specification.

        See https://pydantic-docs.helpmanual.io/usage/model_config/
        for details.
        """

        case_sensitive = True


class Settings(SystemSettings, FileSettings):
    """Merge two sub setting types."""

    def create_default_config_file(self) -> None:
        """Create a file to store the config."""
        config_dict = {}
        for key in FileSettings.__fields__:
            value = self.__getattribute__(key)
            if isinstance(value, Path) or isinstance(
                value, SupportedOutputFormat
            ):
                config_dict[key] = str(value)
            else:
                config_dict[key] = value

        with open(self.CONFIG_FILENAME, "w") as config_file:
            yaml.dump(config_dict, config_file)

    def set_verbosity(self, verbose_count: int) -> None:
        """
        Interpret the verbosity option count.

        Set the log levels accordingly.
        The used log level is also stored in the settings.

        Args:
            verbose_count (int): The amount of verbose option triggers.
        """
        verbosity_options: List[int] = [
            logging.ERROR,
            logging.WARNING,
            logging.INFO,
            logging.DEBUG,
        ]

        max_index: int = len(verbosity_options) - 1

        # Clamp verbose_count to accepted values
        # Note that it shall not be possible to unset the verbosity.
        option_index: int = (
            0
            if verbose_count < 0
            else max_index
            if verbose_count > max_index
            else verbose_count
        )

        new_level: int = verbosity_options[option_index]

        logging.basicConfig(
            level=new_level,
            format="%(asctime)s "
            "[%(levelname)-8s] "
            "%(module)s.%(funcName)s(): "
            "%(message)s",
        )

        self.VERBOSITY = new_level

    def load_config_file(self) -> None:
        """Return an instance of Settings."""
        # if config file exists, load settings from it, otherwise return
        # default
        if Path.is_file(self.CONFIG_FILENAME):
            logging.debug(f"Loading '{self.CONFIG_FILENAME}' as config.")
            with open(self.CONFIG_FILENAME, "r") as config_file:
                config_dict = yaml.load(config_file, Loader=yaml.FullLoader)
            logging.debug(f"Parsing '{config_dict}' as config.")
            for key in config_dict:
                value = config_dict[key]
                logging.debug(f"handling '{key}:{value}'")
                # cast as type, to preserve the type.
                # otherwise paths are getting replaced with strings
                setting_type: type = type(self.__getattribute__(key))
                logging.debug(f"type is '{setting_type}'")
                if setting_type == SupportedOutputFormat:
                    self.__setattr__(
                        key, SupportedOutputFormat.from_str(value)
                    )
                else:
                    self.__setattr__(key, setting_type(value))

            # because assembling the output path is done during initialization,
            # we need to rerun it
            self.ANALYSIS_OUTPUT_PATH = SystemSettings.assemble_output_path(
                self.ANALYSIS_OUTPUT_PATH, self.__dict__
            )
        else:
            logging.debug("No config file present. Keeping default values")
