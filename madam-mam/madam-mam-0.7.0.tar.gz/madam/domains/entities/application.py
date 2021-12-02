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
Madam application data module
"""
from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple, Optional
from uuid import UUID

from madam.domains.entities.job import Job

TABLE_NAME = "applications"

STATUS_RUNNING = "running"
STATUS_COMPLETE = "complete"
STATUS_ABORTED = "aborted"
STATUS_ERROR = "error"
STATUS_CONTAINER_ERROR = "container_error"


@dataclass
class Application:
    """
    Madam Application data class
    """

    id: UUID
    name: str
    version: str
    arguments: str
    start_at: datetime
    end_at: Optional[datetime]
    status: str
    logs: Optional[str]
    container_id: Optional[str]
    container_error: Optional[str]
    job: Job

    @property
    def container_name(self):
        """
        container_name dynamic property

        Return name+ "_" + id

        :return:
        """
        return f"{self.name}_{self.id}"


class AgentApplication(NamedTuple):
    """
    AgentApplication class to list applications in Agent class
    """

    name: str
    version: str


class ApplicationError(Exception):
    """
    ApplicationError exception class
    """


class ApplicationAborted(Exception):
    """
    ApplicationAborted exception class
    """
