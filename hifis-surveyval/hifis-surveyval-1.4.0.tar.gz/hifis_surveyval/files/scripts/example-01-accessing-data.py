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

"""This example script demonstrates accessing metadata and data of a survey."""
from pathlib import Path
from typing import Optional

from pandas import DataFrame, Series

from hifis_surveyval.data_container import DataContainer
from hifis_surveyval.hifis_surveyval import HIFISSurveyval
from hifis_surveyval.models.answer_option import AnswerOption
from hifis_surveyval.models.question import Question
from hifis_surveyval.models.question_collection import QuestionCollection


def run(hifis_surveyval: HIFISSurveyval, data: DataContainer):
    """
    Execute example script that illustrates how to access metadata and data.

    This script in one of a series of example scripts. These examples
    demonstrate the API of the HIFIS-Surveyval Framework. They illustrate the
    process of retrieving data, manipulating data and finally plotting data.

    This particular script is about accessing metadata and data of a survey.

    Please note that the HIFIS-Surveyval Framework does not replace data
    analysis libraries like _Pandas_ which is heavily used for data analysis
    tasks that arise in a survey analysis. In order to dive into the use cases
    and benefits of Pandas you can find a lot of learning material online and
    on the Pandas webpage: https://pandas.pydata.org/
    """
    print("Example analysis script name: " + Path(__file__).stem)

    ###
    # NOTE ON PYTHON TYPE HINTING FOR NOVICE PYTHONISTS:
    #
    # Please be aware that the example scripts use Python's type hinting
    # feature. Using this feature is completely optional in Python, but using
    # type hints has some very nice advantages when developing Python scripts.
    # We recommend using them in your Python scripts.
    # The basic syntax is the following: <variable_name>: <datatype> = <value>
    # These are some very basic examples of type hinting in Python to get you
    # started:
    #
    # my_age: int = 42
    # my_height: float = 1.8
    # my_name: str = "John"
    # my_list: List[int] = [1, 2, 3]
    # my_dict: Dict[str, str] = {"age": "42", "height": "1.8", "name": "John"}
    # my_dataframe: DataFrame = DataFrame()
    # my_series: Series = Series()
    # my_collection: QuestionCollection = data.collection_for_id("Q001")
    # my_question: Question = data.question_for_id("Q001/_")
    ###

    ###
    # CONCEPTS USED THAT YOU NEED TO KNOW:
    #
    # QuestionCollections, Questions and AnswerOptions are fundamental concepts
    # used in this framework and are organized in a hierarchy.
    # QuestionCollections are a set of Questions that group Questions by a
    # specific topic. Questions can not exist on their own. On the other hand,
    # Questions may contain AnswerOptions which represent pre-defined possible
    # answers to the respective Questions. These AnswerOptions can not exist
    # on their own as well.
    #
    # QuestionCollections, Questions and AnswerOptions have IDs. As in the
    # examples below they can be used to query for those objects. The IDs are
    # taken from the metadata YAML file and correspond to the header row of
    # the CSV data file containing the survey answers that you exported from
    # the survey tool. It is recommended to use LimeSurvey as a tool to conduct
    # your surveys that you would like to analyse with the HIFIS-Surveyval
    # Framework.
    #
    # LimeSurvey can be configured so that the IDs in LimeSurvey adhere to
    # the following naming conventions: The ID of a QuestionCollection in
    # these examples scripts starts with the letter "Q", the ID of a Question
    # with the letters "SQ" and the ID of an AnswerOption with letter "A".
    # These letters are followed by three digits to give them an unique number,
    # e.g. "Q001", "SQ001", or "A001". This naming convention is not mandatory,
    # you can use any unique IDs within your survey and for your analysis
    # that fit your needs. Configure your survey tool accordingly and put
    # those IDs that need to be contained in the header row of your CSV data
    # file also into your metadata YAML file.
    #
    # Furthermore, due to the relation between QuestionCollections, Questions,
    # and AnswerOptions, IDs are compound IDs. That means they are
    # concatenated by a specific character, the so called HIERARCHY_SEPARATOR
    # which is the character "/" (slash) by default. In order to give examples
    # of these compound IDs, an ID of a QuestionCollection might be "Q001", an
    # ID of a Question might be "Q001/SQ001", and the ID of an AnswerOption
    # might be "Q001/SQ001/A001". The individual IDs are called "Short IDs"
    # and the compound IDs are called "Full IDs" in this framework.
    #
    # Also, when using LimeSurvey for your surveys, the CSV data export might
    # contain IDs in the header row that are just QuestionCollection IDs
    # without the HIERARCHY_SEPARATOR and Question ID as a suffix, e.g.
    # "Q001" instead of "Q001/SQ001". In order to mark this situation given
    # in the CSV data file, we are using the "_" (underscore) character as the
    # short ID of the Question. Consequently, the full ID of a Question might
    # be "Q001/_" instead of "Q001/SQ001" and the full ID of an AnswerOption
    # might be "Q001/_/A001" instead of "Q001/SQ001/A001".
    ###

    ###
    # The DataContainer can be used to retrieve a QuestionCollection, a
    # Question, or an AnswerOption object by providing their IDs.
    ###

    ###
    # In order to get a QuestionCollection object you can query for it using
    # the DataContainer and passing in a QuestionCollection ID to the
    # respective method.
    ###
    topic_centers: QuestionCollection = data.collection_for_id("Q001")
    print("1) ===== Get a QuestionCollection =====")
    hifis_surveyval.printer.pretty_print(topic_centers)

    ###
    # Once a QuestionCollection object is at hand the full ID can be retrieved.
    ###
    topic_centers_full_id: str = topic_centers.full_id
    print("2) ===== ID of a QuestionCollection =====")
    hifis_surveyval.printer.pretty_print(topic_centers_full_id)

    ###
    # A text of a QuestionCollection can be translated into different supported
    # languages specified by an IETF language tag which consists of the ISO
    # 693-1 two-letter language codes and a two-letter region specifier
    # concatenated by a dash. These translations are given in the metadata.
    ###
    topic_centers_text: str = topic_centers.text("en-GB")
    print("3) ===== Translated text of a QuestionCollection =====")
    hifis_surveyval.printer.pretty_print(topic_centers_text)

    ###
    # A text of a QuestionCollection can also be represented by its label
    # in cases where the full translation of the title is too long and not
    # concise enough.
    ###
    topic_centers_label: str = topic_centers.label
    print("4) ===== Label of a QuestionCollection =====")
    hifis_surveyval.printer.pretty_print(topic_centers_label)

    ###
    # In the context of a QuestionCollection object you can also retrieve
    # specific Question objects. Because of the unambiguity, the ID can be
    # shorter leaving out the ID part of the QuestionCollection, only using
    # the short ID of the Question.
    ###
    center_choices: Question = topic_centers.question_for_id("_")
    print("5) ===== Get a Question from a QuestionCollection =====")
    hifis_surveyval.printer.pretty_print(center_choices)

    ###
    # In the same way as for QuestionCollections you can query for Questions
    # by giving the full ID of a Question and pass it to the respective method.
    ###
    center_choices: Question = data.question_for_id("Q001/_")
    print("6) ===== Get a Question =====")
    hifis_surveyval.printer.pretty_print(center_choices)

    ###
    # Given a Question object the full ID can be retrieved.
    ###
    center_choices_full_id: str = center_choices.full_id
    print("7) ===== ID of a Question =====")
    hifis_surveyval.printer.pretty_print(center_choices_full_id)

    ###
    # A text of a Question can also be translated into different supported
    # languages specified by the ISO 693-1 two-letter language codes.
    ###
    center_choices_text: str = center_choices.text("en-GB")
    print("8) ===== Translated text of a Question =====")
    hifis_surveyval.printer.pretty_print(center_choices_text)

    ###
    # A text of a Question can also be represented by its label in cases where
    # the full translation of the title is too long and not concise enough.
    ###
    center_choices_label: str = center_choices.label
    print("9) ===== Label of a Question =====")
    hifis_surveyval.printer.pretty_print(center_choices_label)

    ###
    # AnswerOption objects are the answers that can be given by survey
    # participants to a particular Question. They are the actual data
    # collected by a survey. AnswerOptions are identified by an ID that
    # consists of the letter "A" and three digits to give each AnswerOption
    # a number, e.g. "A001".
    ###
    answer: AnswerOption = center_choices._answer_options["A001"]
    print("10) ===== Get an AnswerOption from a Question =====")
    hifis_surveyval.printer.pretty_print(answer)

    ###
    # Based on an AnswerOption object the full ID can be retrieved which is
    # made up of a Question ID and an AnswerOption ID separated by the
    # HIERARCHY_SEPARATOR, e.g. "SQ001/A001".
    ###
    answer_full_id: str = answer.full_id
    print("11) ===== ID of an AnswerOption =====")
    hifis_surveyval.printer.pretty_print(answer_full_id)

    ###
    # A text of an AnswerOption can also be translated into different supported
    # languages specified by the ISO 693-1 two-letter language codes.
    ###
    answer_text: str = answer.text("en-GB")
    print("12) ===== Translated text of an AnswerOption =====")
    hifis_surveyval.printer.pretty_print(answer_text)

    ###
    # A text of an AnswerOption can also be represented by its label
    # in cases where the full translation of the title is too long and not
    # concise enough.
    ###
    answer_label: str = answer.label
    print("13) ===== Label of an AnswerOption =====")
    hifis_surveyval.printer.pretty_print(answer_label)

    ###
    # Accessing data/answers of a Question given by survey participants can be
    # done by the participant ID/row-index. Please note that these IDs/indices
    # are non-continuous.
    ###
    given_answer: Optional[object] = center_choices.answers["1"]
    print("14) ===== Access given answers =====")
    hifis_surveyval.printer.pretty_print(given_answer)

    ###
    # A DataFrame object is a table-like data structure with header columns,
    # indexed rows and cells taking up the actual data. The DataFrame data
    # structure is provided by Pandas - a data analysis library. It is meant
    # as a base format in this survey analysis framework and is therefore
    # heavily used by it. In order to get a DataFrame object the DataContainer
    # object offers a method to do so. As an argument the method accepts a
    # list of QuestionCollection IDs. The resulting DataFrame object contains
    # as many columns as there are Questions in the selected
    # QuestionCollections and each cell contains an answer to a Question.
    ###
    data_centers: DataFrame = data.data_frame_for_ids(["Q001", "Q002"])
    print("15) ===== DataFrame of QuestionCollections =====")
    hifis_surveyval.printer.print_dataframe(data_centers)

    ###
    # Another way to get a DataFrame of a specific QuestionCollection is to
    # use the respective method offered by a QuestionCollection object.
    ####
    data_centers_topic: DataFrame = topic_centers.as_data_frame()
    print("16) ===== DataFrame of a QuestionCollection =====")
    hifis_surveyval.printer.print_dataframe(data_centers_topic)

    ###
    # Pandas also provides a table-like data structure with only one column
    # which is called Series.
    ###
    data_center_choices: Series = center_choices.as_series()
    print("17) ===== Series of a Question =====")
    hifis_surveyval.printer.print_dataframe(data_center_choices)
