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
This module provides the definitions for a data container.

The container is meant to serve as the data source for the individual analysis
functions.

.. currentmodule:: hifis_surveyval.data_container
.. moduleauthor:: HIFIS Software <software@hifis.net>
"""
import logging
from logging import debug, warning
from typing import Dict, List, Set, Union

import pandas
from pandas import DataFrame

from hifis_surveyval.core.settings import Settings
from hifis_surveyval.models.mixins.yaml_constructable import YamlDict, YamlList
from hifis_surveyval.models.question import Question
from hifis_surveyval.models.question_collection import QuestionCollection


class DataContainer(object):
    """
    The data container holds the data read from the command line.

    All data is grouped into question collections, which in turn hold the
    questions.
    During the loading, the DataContainer will keep track of answer sets
    which contradict the validation rules set in the metadata (e.g. no
    answer being given despite being mandatory.
    """

    def __init__(self, settings: Settings):
        """
        Set up an empty data container.

        Args:
            settings:
                An object representing the current application settings.
        """
        self._survey_questions: Dict[str, QuestionCollection] = {}
        self._invalid_answer_sets: Set[str] = set()
        # Track participant IDs with invalid answer sets.
        self._settings = settings

    @property
    def survey_questions(self) -> List[QuestionCollection]:
        """
        Obtain all survey questions stored in the data container.

        Returns:
            A list of QuestionCollections that contain all the survey
            questions.
        """
        return list(self._survey_questions.values())

    @property
    def invalid_answer_sets(self) -> Set[str]:
        """
        Get all participants who gave invalid answers.

        Returns:
            A set with the IDs of participants who had their answers marked
            as invalid.
        """
        return self._invalid_answer_sets

    def load_metadata(self, yaml: Union[YamlList, YamlDict]) -> None:
        """
        Load additional metadata from YAML data.

        If the given yaml is valid, the received metadata will be added to the
        known survey questions.
        QuestionCollections that fail to parse will not be added to the survey
        questions and the exception will instead be logged as a warning.
        It is safe to repeatedly call this function, if multiple sources for
        metadata need to be processed.

        Args:
            yaml:
                Either a list of YamlDictionaries or a single YamlDictionary.
                Each YamlDictionary is expected to hold a QuestionCollection,
                Otherwise parsing will fail.
        """
        if not isinstance(yaml, list):
            # in case this is a single value put it in the list for the
            # one-size-fits-all solution below
            yaml = [yaml]

        for new_collection_data in yaml:
            try:
                self._add_collection_from_yaml(new_collection_data)
            except Exception as thrown_exception:
                warning(f"Error while parsing metadata: {thrown_exception}")

    def _add_collection_from_yaml(self, new_collection_yaml: YamlDict) -> None:
        """
        Create a new question collection from YAML and add it to survey data.

        Args:
            new_collection_yaml:
                A YAML mapping containing the data for one question collection.
        """
        new_collection = QuestionCollection.from_yaml_dictionary(
            new_collection_yaml, settings=self._settings
        )
        if new_collection.full_id in self._survey_questions:
            raise ValueError(
                "Attempt to add QuestionCollection " "with duplicate ID"
            )
        self._survey_questions[new_collection.full_id] = new_collection
        debug(f"{new_collection.full_id} added successfully")

    def load_survey_data(self, csv_data: List[List[str]]) -> None:
        """
        Load survey data as given in a CSV file.

        The data is expected to be given in such a way that the outer list
        represents the rows and the inner list the columns within each row
        """
        # Separate the header so it does not get in the way of processing later
        header: List[str] = csv_data[0]
        body: List[List[str]] = csv_data[1:]

        question_cache: Dict[int, Question] = {}
        """
            The question cache associates column indices with questions.
            It is here to avoid having to constantly look up the questions all
            over again. This expects that in each row the indices for the
            questions are identical, which, given the input is CSV data,
            should be the case.
        """

        # Step 0: Find the column for the participant IDs
        id_column_index = header.index(self._settings.ID_COLUMN_NAME)

        # Step 1: Find the Question for each of the headings
        for index in range(0, len(header)):
            if index == id_column_index:
                # no need to check this, it will not be a question
                continue

            potential_question_id = header[index]

            # Replace separator DATA_ID_SEPARATOR by separator
            # HIERARCHY_SEPARATOR before working with full Question IDs
            # in order to use an unambiguous and unique character to separate
            # QuestionCollection ID and Question ID.
            if self._settings.DATA_ID_SEPARATOR in potential_question_id:
                potential_question_id = potential_question_id.replace(
                    self._settings.DATA_ID_SEPARATOR,
                    self._settings.HIERARCHY_SEPARATOR
                )
                header[index] = potential_question_id
                # Update the cached header, for later cross referencing.
                # (This does not touch the actual CSV file header in any way)

            # Limesurvey has that thing where questions may be at the top
            # level (i.e. not within a collection) but still named as if
            # they were a collection. This is not possible in the
            # metadata. This corner case is handled here by appending the
            # anonymous question identifier to the potential_question_id.
            # The underscore character has been chosen on purpose and as an
            # indicator for this special case because there won't be any
            # clashes with the question IDs allowed by Limesurvey and hence
            # there won't be any naming confusion introduced here.
            if self._settings.HIERARCHY_SEPARATOR not in potential_question_id:
                potential_question_id += self._settings.HIERARCHY_SEPARATOR
                potential_question_id += self._settings.ANONYMOUS_QUESTION_ID
                header[index] = potential_question_id

            # Handle the regular case
            try:
                question = self.question_for_id(potential_question_id)
                question_cache[index] = question
            except (KeyError, IndexError):
                logging.error(
                    f"While parsing answers for {potential_question_id}: "
                    f"Question unknown, check the metadata"
                )
                continue

        assert id_column_index not in question_cache

        # Step 2: Check if all questions are present in the header
        for question_collection in self._survey_questions.values():
            for question in question_collection.questions:
                if question.full_id not in header:
                    logging.warning(f"Question {question.full_id} was in "
                                    f"metadata but not in the CSV file")

        # Step 3: Iterate through each row and insert the values for answer
        for row in body:
            participant_id = row[id_column_index]

            for (question_index, question) in question_cache.items():
                answer: str = row[question_index]
                try:
                    question.add_answer(
                        participant_id=participant_id,
                        value_text=answer
                    )
                except (KeyError, ValueError) as error:
                    warning(
                        f"When loading CSV data for {question.full_id}:"
                        f" {error}"
                    )

    def collection_for_id(self, full_id: str) -> QuestionCollection:
        """
        Query for a given question collection given by its full ID.

        Args:
            full_id:
                The full ID of the question collection to be returned.
        Returns:
            The question collection for the given ID.
        Raises:
            KeyError - if the collection for the given ID could not be found.
        """
        return self._survey_questions[full_id]

    def question_for_id(self, full_id: str) -> Question:
        """
        Query for a given question given by its full ID.

        This is a shorthand for querying questions directly.

        Args:
            full_id:
                The full ID of the question to be returned.
        Returns:
            The question for the given ID.
        Raises:
            KeyError:
                If either the collection or the question for the given ID
                could not be found.
        """
        parts: List[str] = full_id.split(self._settings.HIERARCHY_SEPARATOR)
        collection_id = parts[0]
        question_id = parts[1]
        collection = self.collection_for_id(collection_id)
        return collection.question_for_id(question_id)

    def remove_invalid_answer_sets(self) -> None:
        """
        Remove answer sets that were marked as invalid.

        The answers are removed on a per-participant basis.
        """
        for collection in self._survey_questions.values():
            collection.remove_answers(self._invalid_answer_sets)

    def mark_answers_invalid(self, participant_ids: Set[str]) -> None:
        """
        Mark the answers given by participants as invalid.

        Args:
            participant_ids:
                The IDs of participants who gave invalid answers.
        """
        self._invalid_answer_sets.update(participant_ids)

    def mark_answers_valid(self, participant_ids: Set[str]) -> None:
        """
        Mark the answers given by participants as valid.

        NOTE: This does not restore previously removed invalid answers.
        Invalid IDs are silently ignored.

        Args:
            participant_ids:
                The IDs of participants for whom answers are to be marked as
                valid.
        """
        self._invalid_answer_sets.difference_update(participant_ids)

    @property
    def question_collection_ids(self) -> List[str]:
        """
        Get the IDs of all question collections.

        Returns:
            A list of question collection IDs as strings.
        """
        return list(self._survey_questions.keys())

    def data_frame_for_ids(self, requested_ids: List[str]) -> DataFrame:
        """
        Compose a Data Frame form a list of question (collection) IDs.

        IDs for which no question or question collection can be found will
        be skipped. These will be logged at debug level.

        Args:
            requested_ids:
                A list of full question or question collection IDs,
                which are to be composed by participant into a single data
                frame.
        Returns:
            A single data frame containing the answers of all participants
            for the given questions / question collections.
        """
        frame_pieces: List[DataFrame] = []

        for piece_id in requested_ids:
            try:
                frame_pieces.append(self._frame_for_id(piece_id))
            except ValueError as error:
                logging.debug(error)
                continue

        return pandas.concat(frame_pieces, axis=1)

    def _frame_for_id(self, piece_id) -> DataFrame:
        """
        Obtain a data frame representation for a Question (Collection) ID.

        This is a helper method used to transform either questions or
        question collections into data frames based on their ID. It a
        shortcut to be used in data_frame_for_ids() and not meant to be
        called by the user. Use the appropriate functions of questions and
        collections instead.
        Args:
            piece_id:
                The full ID of either a question or question collection.
        Returns:
            A data frame matching the answers given per participant for the
            question or question collection identified by the provided ID.
        Raises:
            ValueError:
                When no Question or QuestionCollection with the given ID
                exists.
        """
        try:
            return self.collection_for_id(piece_id).as_data_frame()
        except KeyError:
            pass

        try:
            return DataFrame(self.question_for_id(piece_id).as_series())
        except KeyError:
            pass

        raise ValueError(
            f"{piece_id} is not a valid " f"question / collection ID"
        )
