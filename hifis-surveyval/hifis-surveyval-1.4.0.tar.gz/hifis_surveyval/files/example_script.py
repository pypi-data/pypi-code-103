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
This is an example script for an analysis.

It is a file payload of the package `hifis_surveyval`.
"""

from hifis_surveyval.data_container import DataContainer
from hifis_surveyval.hifis_surveyval import HIFISSurveyval


def run(hifis_surveyval: HIFISSurveyval, data: DataContainer):
    """Execute example script."""
    # print all loaded question IDs
    for question in data.question_collection_ids:
        print(question)

    # get a pandas dataframe for one or more question collection IDs
    question_collection_ids = ["Q001", "Q002", "Q009"]
    dataframe = data.data_frame_for_ids(question_collection_ids)
    hifis_surveyval.printer.print_dataframe(dataframe)

    # get a pandas dataframe for all questions collections
    dataframe = data.data_frame_for_ids(data.question_collection_ids)
    hifis_surveyval.printer.print_dataframe(dataframe)
