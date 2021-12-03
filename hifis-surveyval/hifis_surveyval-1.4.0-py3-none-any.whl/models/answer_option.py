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

"""This module contains a class to represent survey answers."""
import logging
from typing import Optional as typing_Optional, Generic

from schema import Schema, Optional

from hifis_surveyval.core.settings import Settings
from hifis_surveyval.models.answer_types import AnswerType
from hifis_surveyval.models.mixins.mixins import HasLabel, HasText, HasID
from hifis_surveyval.models.mixins.yaml_constructable import (
    YamlConstructable,
    YamlDict,
)
from hifis_surveyval.models.translated import Translated


class AnswerOption(
    Generic[AnswerType],
    YamlConstructable,
    HasID,
    HasLabel,
    HasText
):
    """The AnswerOption models allowed answers for a specific Question."""

    token_ID = "id"
    token_VALUE = "value"

    schema = Schema(
        {
            token_ID: str,
            HasLabel.YAML_TOKEN: str,
            HasText.YAML_TOKEN: dict,
            Optional(token_VALUE, default=None): object
        }
    )

    def __init__(
            self,
            parent_id: str,
            option_id: str,
            text: Translated,
            label: str,
            settings: Settings,
            value: typing_Optional[AnswerType],
    ) -> None:
        """
        Create an answer option from the metadata.

        Args:
            parent_id:
                The full ID of the question this answer option belongs to.
            option_id (str):
                A unique string identifying the answer.
            text:
                A Translated object containing the texts that represent the
                answer option across various languages.
            label:
                A short string used to represent the answer option in plotting.
            settings:
                An object reflecting the application settings.
            value:
                (Optional) A value to represent the AnswerOption, e.g. for
                sorting, calculations or to represent an underlying value if
                the label can not easily be cast to the intended AnswerType.
        """
        super(AnswerOption, self).__init__(
            object_id=option_id,
            parent_id=parent_id,
            label=label,
            translations=text,
            settings=settings
        )
        self._value: typing_Optional[AnswerType] = value

    def __str__(self) -> str:
        """
        Generate a string representation of the answer option.

        Returns:
                String representation of the answer.
        """
        return f"{self.full_id}: {self._label}"

    @property
    def value(self) -> typing_Optional[AnswerType]:
        """
        Access the underlying value type, if present.

        Returns:
            The underlying value if it is defined, None otherwise.
        """
        return self._value

    @staticmethod
    def _from_yaml_dictionary(yaml: YamlDict, **kwargs) -> "AnswerOption":
        """
        Generate a new AnswerOption-instance from YAML data.

        Args:
            yaml:
                A YAML dictionary describing the AnswerOption
            **kwargs:
                parent_id:
                    The ID of the Question-instance to which the newly
                    generated AnswerOption belongs.
                settings:
                    The used settings instance
                answer_type:
                    The data type of which the answer value should be.
        Returns:
            A new AnswerOption containing the provided data
        """
        parent_id = kwargs["parent_id"]
        settings: Settings = kwargs["settings"]
        answer_type: type = kwargs["answer_type"]
        option_id = yaml[AnswerOption.token_ID]

        label = yaml[HasLabel.YAML_TOKEN]
        yaml_value = yaml[AnswerOption.token_VALUE]

        value = None
        if yaml_value is not None:
            value = yaml_value
        else:
            # If no explicit value was given, try to infer it from the label
            try:
                value = answer_type(label)
            except ValueError:
                logging.error(
                    f"Could not infer answer option value from label for "
                    f"{parent_id}/{option_id}: \"{label}\" (wanted to cast to"
                    f" {answer_type.__name__})"
                )

        return AnswerOption[answer_type](
            parent_id=parent_id,
            option_id=option_id,
            label=label,
            text=Translated.from_yaml_dictionary(
                yaml[HasText.YAML_TOKEN]
            ),
            settings=settings,
            value=value
        )
