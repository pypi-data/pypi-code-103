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
Madam timers domain module
"""
import copy
import uuid
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Event
from time import sleep
from typing import Dict, List, Optional, Union

from madam.domains.entities.events import TimerEvent
from madam.domains.entities.runner import TimerRunner
from madam.domains.entities.timer import (
    STATUS_ABORTED,
    STATUS_COMPLETE,
    STATUS_RUNNING,
    CyclicTimer,
    DateTimer,
)
from madam.domains.entities.workflow import Workflow
from madam.domains.events import EventDispatcher
from madam.domains.interfaces.repository.timers import TimerRepositoryInterface
from madam.domains.workflow_instances import WorkflowInstances
from madam.libs import iso8601


class Timers:
    """
    Madam Timers domain class
    """

    def __init__(
        self,
        repository: TimerRepositoryInterface,
        workflow_instances: WorkflowInstances,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Timers domain

        :param repository: TimerRepository adapter instance
        :param workflow_instances: WorkflowInstances domain instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.workflow_instances = workflow_instances
        self.register: Dict[uuid.UUID, TimerRunner] = {}
        self.event_dispatcher = event_dispatcher

        # get running timers
        timers = self.list(status=STATUS_RUNNING)
        # restart timers
        for timer in timers:
            self._register_runner_and_start(timer)

    def create_date_timer(
        self, workflow: Workflow, date: datetime, variables: Optional[dict] = None
    ) -> DateTimer:
        """
        Create a DateTimer with an entry in database

        :param workflow: Workflow the instance is created upon
        :param date: Date to create a DateTimer
        :param variables: Initial variables (default=None)
        :return:
        """
        timer = DateTimer(
            id=uuid.uuid4(),
            start_at=datetime.now(),
            end_at=None,
            status=STATUS_RUNNING,
            input=variables,
            workflow=workflow,
            date=date,
        )
        # Create new entry in database
        self.repository.create_date_timer(timer)

        # dispatch event
        event = TimerEvent(
            TimerEvent.EVENT_TYPE_CREATE,
            copy.copy(timer),
        )
        self.event_dispatcher.dispatch_event(event)

        return timer

    def create_cyclic_timer(
        self,
        workflow: Workflow,
        repeat: int,
        interval: timedelta,
        variables: Optional[dict] = None,
    ) -> CyclicTimer:
        """
        Create a CyclicTimer with an entry in database

        :param workflow: Workflow the instance is created upon
        :param repeat: Repeat count with 0 for infinite to create a CyclicTimer
        :param interval: Interval time between workflow instances to create a CyclicTimer
        :param variables: Initial variables (default=None)
        :return:
        """
        timer = CyclicTimer(
            id=uuid.uuid4(),
            start_at=datetime.now(),
            end_at=None,
            status=STATUS_RUNNING,
            input=variables,
            workflow=workflow,
            repeat=repeat,
            interval=interval,
        )
        # Create new entry in database
        self.repository.create_cyclic_timer(timer)

        # dispatch event
        event = TimerEvent(
            TimerEvent.EVENT_TYPE_CREATE,
            copy.copy(timer),
        )
        self.event_dispatcher.dispatch_event(event)

        return timer

    def read(self, id_: uuid.UUID) -> Union[CyclicTimer, DateTimer]:
        """
        Get a Timer object by its id_.

        :param id_: Id of the timer
        :return:
        """
        return self.repository.read(id_)

    def update(self, timer: Union[CyclicTimer, DateTimer], **kwargs):
        """
        Update kwargs fields of timer

        :param timer: Timer instance
        :return:
        """
        # update object
        for key, value in kwargs.items():
            if hasattr(timer, key):
                setattr(timer, key, value)

        # update entry in database
        self.repository.update(timer.id, **kwargs)

        # dispatch event
        event = TimerEvent(
            TimerEvent.EVENT_TYPE_UPDATE,
            copy.copy(timer),
        )
        self.event_dispatcher.dispatch_event(event)

    def delete(self, timer: Union[CyclicTimer, DateTimer]):
        """
        Delete timer from database

        :param timer: Timer instance
        :return:
        """
        # delete entry in database
        self.repository.delete(timer.id)

        # dispatch event
        event = TimerEvent(
            TimerEvent.EVENT_TYPE_DELETE,
            copy.copy(timer),
        )
        self.event_dispatcher.dispatch_event(event)

    def list(
        self,
        offset: int = 0,
        limit: int = 1000,
        sort_column: str = "start_at",
        sort_ascending: bool = True,
        status: str = None,
        workflow: Optional[Workflow] = None,
    ) -> List[Union[DateTimer, CyclicTimer]]:
        """
        Return a list of Timer objects

        :param offset: First entry offset (default=0)
        :param limit: Number of entries (default=1000)
        :param sort_column: Sort column name (default="start_at")
        :param sort_ascending: Ascending sort order (default=True), descending if False
        :param status: Status constant to filter by, None for all status (default=None)
        :param workflow: Parent workflow to filter by (default=None)
        :return:
        """
        return self.repository.list(
            offset, limit, sort_column, sort_ascending, status, workflow
        )

    def count(self, status: str = None, workflow: Workflow = None) -> int:
        """
        Return total count of timers

        :param status: Filter by status (default=None)
        :param workflow: Filter by parent Workflow (default=None)
        :return:
        """
        return self.repository.count(status, workflow)

    def start(self, workflow: Workflow, variables: Optional[dict] = None) -> bool:
        """
        Create and start timer

        :param workflow: Parent Workflow object
        :param variables: Initial variables (default=None)
        :return:
        """
        if workflow.timer is None:
            return False
        # parse timer ISO 8601 expression
        result = iso8601.parse(workflow.timer)
        if isinstance(result, tuple):
            repeat, interval = result
            # create and register Timer (to be able to abort it)
            cyclic_timer = self.create_cyclic_timer(
                workflow, repeat, interval, variables
            )
            self._register_runner_and_start(cyclic_timer)
        else:
            # create and register Timer (to be able to abort it)
            date_timer = self.create_date_timer(workflow, result, variables)
            self._register_runner_and_start(date_timer)

        return True

    def start_cyclic(self, timer: CyclicTimer, abort_event: Event):
        """
        Start cyclic timer

        :param timer: CyclicTimer instance
        :param abort_event: threading Event instance
        :return:
        """
        repeat = timer.repeat
        interval = timer.interval
        if repeat > 0:
            count = 1
            # limited loop
            while count <= repeat and not abort_event.is_set():
                self.workflow_instances.start(
                    timer.workflow,
                    timer.input,
                )
                sleep(interval.seconds)
                count += 1

            # if timer aborted
            if abort_event.is_set():
                timer.status = STATUS_ABORTED
            else:
                timer.status = STATUS_COMPLETE
            self.update(timer, status=timer.status, end_at=datetime.now())
        else:
            # infinite loop
            while not abort_event.is_set():
                self.workflow_instances.start(
                    timer.workflow,
                    timer.input,
                )
                sleep(interval.seconds)

            # timer status aborted
            timer.status = STATUS_ABORTED
            self.update(timer, status=timer.status, end_at=datetime.now())

    def start_date(self, timer: DateTimer, abort_event: Event):
        """
        Start date timer

        :param timer: DateTimer instance
        :param abort_event: threading Event instance
        :return:
        """
        datetime_ = timer.date

        before = True
        while before and not abort_event.is_set():
            sleep(1)
            now = datetime.now()
            if now.timestamp() >= datetime_.timestamp():
                before = False

        # if timer aborted
        if abort_event.is_set():
            timer.status = STATUS_ABORTED
        else:
            timer.status = STATUS_COMPLETE

        self.update(timer, status=timer.status, end_at=datetime.now())

        if timer.status == STATUS_COMPLETE:
            self.workflow_instances.start(timer.workflow, timer.input)

    def abort_by_workflow(self, workflow: Workflow):
        """
        Abort running timers of workflow

        :param workflow: Workflow object
        :return:
        """
        timers = self.list(status=STATUS_RUNNING, workflow=workflow)

        for timer in timers:
            self.abort(timer.id)

    def abort(self, timer_id: uuid.UUID):
        """
        Abort timer by ID

        :param timer_id: Timer ID
        :return:
        """
        # set abort_event to inform thread to abort
        self.register[timer_id].abort_event.set()

    def _register_runner_and_start(self, timer: Union[CyclicTimer, DateTimer]):
        """
        Register and start timer

        :param timer: Timer instance
        :return:
        """
        runner = TimerRunner(timer, ThreadPoolExecutor(), None, Event())

        self.register[timer.id] = runner

        if isinstance(timer, CyclicTimer):
            # start cyclic timer in a background thread
            runner.future = runner.executor.submit(
                self.start_cyclic, timer, runner.abort_event
            )
        else:
            # start date timer in a background thread
            runner.future = runner.executor.submit(
                self.start_date, timer, runner.abort_event
            )

        # add callback to delete runner after timer ended
        runner.future.add_done_callback(self._remove_runner)

    def _remove_runner(self, future: Future):
        """
        Remove runner after future is done

        :param future: Future completed
        :return:
        """
        index = None
        for timer_id, runner in self.register.items():
            if runner.future == future:
                index = timer_id

        if index is not None:
            del self.register[index]
