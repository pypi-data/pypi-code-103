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
Madam Runner data class
"""
from concurrent.futures._base import Future
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from multiprocessing import Process
from threading import Event
from typing import Optional, Union

from madam.domains.entities.timer import CyclicTimer, DateTimer
from madam.domains.entities.watchfolder import Watchfolder
from madam.domains.interfaces.bpmn import BPMNEngineInterface


@dataclass
class WorkflowInstanceRunner:
    """
    Madam Runner data class
    """

    bpmn_engine: BPMNEngineInterface
    instance_executor: ThreadPoolExecutor
    future: Optional[Future]


@dataclass
class TimerRunner:
    """
    Madam TimerRunner data class
    """

    timer: Union[CyclicTimer, DateTimer]
    executor: ThreadPoolExecutor
    future: Optional[Future]
    abort_event: Event


@dataclass
class WatchfolderRunner:
    """
    Madam WatchfolderRunner data class
    """

    watchfolder: Watchfolder
    process: Process
