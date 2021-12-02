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
Madam job data module
"""
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from madam.domains.entities.workflow_instance import WorkflowInstance

TABLE_NAME = "jobs"

STATUS_RUNNING = "running"
STATUS_COMPLETE = "complete"
STATUS_ABORTED = "aborted"
STATUS_ERROR = "error"


@dataclass
class Job:
    """
    Madam Job data class
    """

    id: uuid.UUID
    agent_id: str
    agent_type: str
    start_at: datetime
    end_at: Optional[datetime]
    status: str
    headers: Optional[dict]
    input: dict
    output: Optional[dict]
    error: Optional[str]
    workflow_instance: WorkflowInstance
