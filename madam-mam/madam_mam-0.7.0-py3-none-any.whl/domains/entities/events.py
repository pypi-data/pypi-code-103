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
madam events data module
"""
from dataclasses import dataclass
from typing import ClassVar

from madam.domains.entities.application import Application
from madam.domains.entities.job import Job
from madam.domains.entities.timer import Timer
from madam.domains.entities.watchfolder import Watchfolder
from madam.domains.entities.workflow import Workflow
from madam.domains.entities.workflow_instance import WorkflowInstance
from madam.domains.interfaces.events import EventInterface


@dataclass
class WatchfolderEvent(EventInterface):
    """
    WatchfolderEvent class
    """

    type: str
    watchfolder: Watchfolder

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_CREATE: ClassVar[str] = f"{__qualname__}.create"  # type: ignore
    EVENT_TYPE_UPDATE: ClassVar[str] = f"{__qualname__}.update"  # type: ignore
    EVENT_TYPE_DELETE: ClassVar[str] = f"{__qualname__}.delete"  # type: ignore


@dataclass
class WorkflowEvent(EventInterface):
    """
    WorkflowEvent class
    """

    type: str
    workflow: Workflow

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_CREATE: ClassVar[str] = f"{__qualname__}.create"  # type: ignore
    EVENT_TYPE_DELETE: ClassVar[str] = f"{__qualname__}.delete"  # type: ignore


@dataclass
class WorkflowInstanceEvent(EventInterface):
    """
    WorkflowInstanceEvent class
    """

    type: str
    workflow_instance: WorkflowInstance

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_CREATE: ClassVar[str] = f"{__qualname__}.create"  # type: ignore
    EVENT_TYPE_UPDATE: ClassVar[str] = f"{__qualname__}.update"  # type: ignore
    EVENT_TYPE_DELETE: ClassVar[str] = f"{__qualname__}.delete"  # type: ignore


@dataclass
class TimerEvent(EventInterface):
    """
    TimerEvent class
    """

    type: str
    timer: Timer

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_CREATE: ClassVar[str] = f"{__qualname__}.create"  # type: ignore
    EVENT_TYPE_UPDATE: ClassVar[str] = f"{__qualname__}.update"  # type: ignore
    EVENT_TYPE_DELETE: ClassVar[str] = f"{__qualname__}.delete"  # type: ignore


@dataclass
class JobEvent(EventInterface):
    """
    JobEvent class
    """

    type: str
    job: Job

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_CREATE: ClassVar[str] = f"{__qualname__}.create"  # type: ignore
    EVENT_TYPE_UPDATE: ClassVar[str] = f"{__qualname__}.update"  # type: ignore
    EVENT_TYPE_DELETE: ClassVar[str] = f"{__qualname__}.delete"  # type: ignore


@dataclass
class ApplicationEvent(EventInterface):
    """
    ApplicationEvent class
    """

    type: str
    application: Application

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_CREATE: ClassVar[str] = f"{__qualname__}.create"  # type: ignore
    EVENT_TYPE_UPDATE: ClassVar[str] = f"{__qualname__}.update"  # type: ignore
    EVENT_TYPE_DELETE: ClassVar[str] = f"{__qualname__}.delete"  # type: ignore
