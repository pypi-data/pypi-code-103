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
Madam watchfolder data module
"""
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from madam.domains.entities.workflow import Workflow

TABLE_NAME = "watchfolders"

STATUS_RUNNING = "running"
STATUS_STOPPED = "stopped"
STATUS_ERROR = "error"


@dataclass
class Watchfolder:
    """
    Watchfolder data class
    """

    id: uuid.UUID
    path: str
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    status: str
    re_files: Optional[str]
    re_dirs: Optional[str]
    added_workflow: Optional[Workflow]
    added_variables: Optional[dict]
    modified_workflow: Optional[Workflow]
    modified_variables: Optional[dict]
    deleted_workflow: Optional[Workflow]
    deleted_variables: Optional[dict]
    added_items_key: str = "watchfolder"
    modified_items_key: str = "watchfolder"
    deleted_items_key: str = "watchfolder"
