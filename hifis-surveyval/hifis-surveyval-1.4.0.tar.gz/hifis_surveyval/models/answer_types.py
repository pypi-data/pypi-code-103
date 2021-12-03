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
This contains information about the data types supported by answers.

The currently supported types are bool, int, float and str. The type names
are the only valid identifiers in YAML metadata for the data type of questions.
"""
from typing import Dict, TypeVar

VALID_ANSWER_TYPES: Dict[str, type] = {
    valid_type.__name__: valid_type for valid_type in (bool, int, float, str)
}
"""
A mapping from the names of accepted types to the actual types.

This allows to infer the actual types from the string representations present
in the YAML metadata.
"""

AnswerType = TypeVar("AnswerType")
"""
Type variable for the generic type used in AnswerOption.

It may be a placeholder for any of the accepted answer types.
"""
