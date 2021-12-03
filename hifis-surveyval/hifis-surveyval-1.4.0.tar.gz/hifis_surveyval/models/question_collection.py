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
This module contains classes to represent groups of survey questions.

These can be constructed from YAML through the YamlConstructable abstract
class.
"""
from typing import Dict, List, Set
from typing import Optional as typing_Optional
from typing import Union

from pandas import DataFrame, Series, concat
from schema import Optional, Schema

from hifis_surveyval.core.settings import Settings
from hifis_surveyval.models.mixins.mixins import (
    HasLabel, HasText, HasID, HasMandatory,
)
from hifis_surveyval.models.mixins.yaml_constructable import (
    YamlConstructable, YamlDict,
)
from hifis_surveyval.models.question import Question
from hifis_surveyval.models.translated import Translated


class QuestionCollection(
    YamlConstructable,
    HasID,
    HasLabel,
    HasText,
    HasMandatory
):
    """
    QuestionCollections group a set of questions into a common context.

    This kind of question has no answers by itself. These are to be found in
    the according sub-questions.
    """

    token_ID = "id"
    token_QUESTIONS = "questions"

    schema = Schema(
        {
            token_ID: str,
            HasLabel.YAML_TOKEN: str,
            HasText.YAML_TOKEN: dict,
            Optional(token_QUESTIONS, default=[]): list,
            Optional(HasMandatory.YAML_TOKEN, default=False): bool,
            Optional(str): object,  # catchall
        }
    )

    def __init__(
        self,
        collection_id: str,
        text: Translated,
        label: str,
        questions: List[Question],
        mandatory: bool,
        settings: Settings,
    ) -> None:
        """
        Initialize an empty question collection.

        It is recommended to refer to from_yaml_dictionary() for constructing
        instances when parsing metadata.

        Args:
            collection_id:
                The unique ID that is to be assigned to the collection.
                Since QuestionCollections have no parent the collection ID
                serves as the full ID as well as the short ID.
            text:
                A Translated object representing the text that describes the
                question collection.
            label:
                A short label that can be used in plotting to represent the
                question collection.
            questions:
                A list of questions that are contained within the question
                collection.
            mandatory:
                Whether there is an answer to at least one of the contained
                questions expected from each participant in order to consider
                the participant's answer data complete.
            settings:
                The settings used by the framework
        """
        super(QuestionCollection, self).__init__(
            object_id=collection_id,
            label=label,
            translations=text,
            is_mandatory=mandatory,
            settings=settings,
        )
        self._questions: Dict[str, Question] = {
            question.short_id: question for question in questions
        }

    @property
    def questions(self) -> List[Question]:
        """
        List all questions in this collection.

        Returns:
            A list with all question objects associated with this collection
        """
        return list(self._questions.values())

    def question_for_id(self, question_short_id: str) -> Question:
        """
        Obtain a question from the collection for a given short ID.

        Args:
            question_short_id:
                The short id used within the collection for this question.
        Returns:
            The question for the given ID.
        Raises:
            KeyError - if no question with the given ID did exist.
        """
        return self._questions[question_short_id]

    def remove_answers(self, participant_ids: Set[str]) -> None:
        """
        Remove the answers by the specified participants.

        Args:
            participant_ids:
                The IDs of the participants whose answers are to be removed.
                Invalid IDs are ignored.
        """
        for question in self._questions.values():
            question.remove_answers(participant_ids)

    def as_data_frame(
        self, exclude_labels: typing_Optional[Union[str, List[str]]] = None
    ) -> DataFrame:
        """
        Gather the answers given to each question as a data frame.

        Args:
            exclude_labels:
                A short label or a list of short labels for questions that
                are to be excluded from the data frame.

        Returns:
            A pandas data frame with participants in the rows and the
            questions of this collection in the columns. The fields in
            the data frame then contain the answer to a question for a
            given participant.
        """
        excluded = []
        if isinstance(exclude_labels, str):
            excluded.append(exclude_labels)
        elif isinstance(exclude_labels, list):
            excluded.extend(exclude_labels)
        # Nothing to do in any other case

        question_series: List[Series] = []
        for (label, question) in self._questions.items():
            if label in excluded:
                continue
            question_series.append(question.as_series())
        return concat(question_series, axis=1)  # Note (0)

    # Note (0) The series are joined row-wise, so each participant in the
    # row labels (aka indexes) is associated with each answer according to
    # the question (Question ID in the column labels).

    @staticmethod
    def _from_yaml_dictionary(
        yaml: YamlDict, **kwargs
    ) -> "QuestionCollection":
        """
        Generate a new QuestionCollection-instance from YAML data.

        Args:
            yaml:
                A YAML dictionary describing the Question

        Keyword Args:
            settings:
                (Required) An object representing the application settings.

        Returns:
            A new Question containing the provided data
        """
        collection_id = yaml[QuestionCollection.token_ID]
        settings = kwargs["settings"]

        questions = [
            Question.from_yaml_dictionary(
                yaml=question_yaml, parent_id=collection_id, settings=settings
            )
            for question_yaml in yaml[QuestionCollection.token_QUESTIONS]
        ]

        text = Translated.from_yaml_dictionary(
            yaml[HasText.YAML_TOKEN]
        )

        return QuestionCollection(
            collection_id=collection_id,
            text=text,
            label=yaml[HasLabel.YAML_TOKEN],
            questions=questions,
            mandatory=yaml[HasMandatory.YAML_TOKEN],
            settings=settings
        )
