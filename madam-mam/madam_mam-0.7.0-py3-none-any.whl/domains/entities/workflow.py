# Copyright 2021 Vincent Texier
#
# This file is part of MADAM.
#
# MADAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MADAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MADAM.  If not, see <https://www.gnu.org/licenses/>.

"""
Madam workflow data module
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

TABLE_NAME = "workflows"


@dataclass
class Workflow:
    """
    Madam Workflow data class
    """

    id: str
    version: int
    name: str
    content: str
    sha256: str
    timer: Optional[str]
    created_at: datetime

    def __repr__(self):
        """
        Return a string representation of Workflow dict

        :return:
        """
        return str(self.__dict__)

    def __eq__(self, other):
        """
        Return True if self equals other

        :param other: Workflow instance
        :return:
        """
        return (
            isinstance(other, Workflow)
            and self.id == other.id
            and self.version == other.version
        )

    def __hash__(self):
        """
        Return hash of object unique composite key

        :return:
        """
        return hash((self.id, self.version))
