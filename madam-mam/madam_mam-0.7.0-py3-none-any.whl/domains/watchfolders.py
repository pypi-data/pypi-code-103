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
Madam watchfolders domain module
"""
import copy
import uuid
from datetime import datetime
from multiprocessing import Process
from typing import Dict, List, Optional

from watchgod import AllWatcher, Change, RegExpWatcher, watch

from madam.domains.entities.events import WatchfolderEvent
from madam.domains.entities.runner import WatchfolderRunner
from madam.domains.entities.watchfolder import (
    STATUS_RUNNING,
    STATUS_STOPPED,
    Watchfolder,
)
from madam.domains.entities.workflow import Workflow
from madam.domains.events import EventDispatcher
from madam.domains.interfaces.repository.watchfolders import (
    WatchfolderRepositoryInterface,
)
from madam.domains.workflows import Workflows


class Watchfolders:
    """
    Madam Watchfolders domain class
    """

    def __init__(
        self,
        repository: WatchfolderRepositoryInterface,
        workflows: Workflows,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init Watchfolders domain

        :param repository: WatchfolderRepository adapter instance
        :param workflows: Workflows domain instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.workflows = workflows
        self.register: Dict[uuid.UUID, WatchfolderRunner] = {}
        self.event_dispatcher = event_dispatcher

        # get running watchfolders
        watchfolders = self.list(status=STATUS_RUNNING)
        # restart watchfolders
        for watchfolder in watchfolders:
            self._register_runner_and_start(watchfolder)

    def create(
        self,
        path: str,
        re_files: Optional[str] = None,
        re_dirs: Optional[str] = None,
        added_workflow: Optional[Workflow] = None,
        added_variables: Optional[dict] = None,
        modified_workflow: Optional[Workflow] = None,
        modified_variables: Optional[dict] = None,
        deleted_workflow: Optional[Workflow] = None,
        deleted_variables: Optional[dict] = None,
        added_items_key: str = "watchfolder",
        modified_items_key: str = "watchfolder",
        deleted_items_key: str = "watchfolder",
    ) -> Watchfolder:
        """
        Create a Watchfolder with an entry in database

        :param path: Path of the folder to watch
        :param re_files: Regular expression to filter files to watch (default=None)
        :param re_dirs: Regular expression to filter directories to watch (default=None)
        :param added_workflow: Workflow instance to start when a file is added (default=None)
        :param added_variables: Initial variables for added_workflow (default=None)
        :param modified_workflow: Workflow instance to start when a file is modified (default=None)
        :param modified_variables: Initial variables for modified_workflow (default=None)
        :param deleted_workflow: Workflow instance to start when a file is deleted (default=None)
        :param deleted_variables: Initial variables for deleted_workflow (default=None)
        :param added_items_key: Key to store added files list in workflow initial variables (default="watchfolder)
        :param modified_items_key: Key to store modified files list in workflow initial variables (default="watchfolder)
        :param deleted_items_key: Key to store deleted files list in workflow initial variables (default="watchfolder)
        :return:
        """
        watchfolder = Watchfolder(
            id=uuid.uuid4(),
            path=path,
            start_at=None,
            end_at=None,
            status=STATUS_STOPPED,
            re_files=re_files,
            re_dirs=re_dirs,
            added_workflow=added_workflow,
            added_variables=added_variables,
            modified_workflow=modified_workflow,
            modified_variables=modified_variables,
            deleted_workflow=deleted_workflow,
            deleted_variables=deleted_variables,
            added_items_key=added_items_key,
            modified_items_key=modified_items_key,
            deleted_items_key=deleted_items_key,
        )

        self.repository.create(watchfolder)

        # dispatch event
        event = WatchfolderEvent(
            WatchfolderEvent.EVENT_TYPE_CREATE,
            copy.copy(watchfolder),
        )
        self.event_dispatcher.dispatch_event(event)

        return watchfolder

    def read(self, id_: uuid.UUID) -> Watchfolder:
        """
        Get a Watchfolder object by its ID

        :param id_: Id of the watchfolder
        :return:
        """
        return self.repository.read(id_)

    def update(self, watchfolder: Watchfolder, **kwargs):
        """
        Update kwargs fields of watchfolder

        :param watchfolder: Watchfolder instance
        :return:
        """
        # update object
        for key, value in kwargs.items():
            if hasattr(watchfolder, key):
                setattr(watchfolder, key, value)

        self.repository.update(watchfolder.id, **kwargs)

        # dispatch event
        event = WatchfolderEvent(
            WatchfolderEvent.EVENT_TYPE_UPDATE,
            copy.copy(watchfolder),
        )
        self.event_dispatcher.dispatch_event(event)

    def delete(self, watchfolder: Watchfolder):
        """
        Delete watchfolder from database

        :param watchfolder: Watchfolder instance
        :return:
        """
        if watchfolder.status == STATUS_RUNNING:
            self.stop(watchfolder.id)

        # delete entry in database
        self.repository.delete(watchfolder.id)

        # dispatch event
        event = WatchfolderEvent(
            WatchfolderEvent.EVENT_TYPE_DELETE,
            copy.copy(watchfolder),
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
    ) -> List[Watchfolder]:
        """
        Return a list of Watchfolder objects

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
        Return total count of watchfolders

        :param status: Filter by status (default=None)
        :param workflow: Filter by Workflow (default=None)
        :return:
        """
        return self.repository.count(status, workflow)

    def start(self, watchfolder: Watchfolder):
        """
        Start watchfolder

        :param watchfolder: Watchfolder instance
        :return:
        """
        if watchfolder.status != STATUS_RUNNING:
            self.update(
                watchfolder, status=STATUS_RUNNING, start_at=datetime.now(), end_at=None
            )

        self._register_runner_and_start(watchfolder)

    def watcher(self, watchfolder):
        """
        Start watcher

        :param watchfolder: Watchfolder instance
        :return:
        """
        watcher_cls = AllWatcher
        watcher_kwargs = None

        # if filter files or directories by regexp
        if watchfolder.re_files is not None or watchfolder.re_dirs is not None:
            # use regexp watcher
            watcher_cls = RegExpWatcher
            # set filters
            watcher_kwargs = {}
            if watchfolder.re_files is not None:
                watcher_kwargs["re_files"] = watchfolder.re_files
            if watchfolder.re_dirs is not None:
                watcher_kwargs["re_dirs"] = watchfolder.re_dirs

        # run watcher
        for changes in watch(
            watchfolder.path, watcher_cls=watcher_cls, watcher_kwargs=watcher_kwargs
        ):
            added_list = []
            modified_list = []
            deleted_list = []
            for event_type, path in changes:
                if (
                    event_type == Change.added
                    and watchfolder.added_workflow is not None
                ):
                    added_list.append(path)
                elif (
                    event_type == Change.modified
                    and watchfolder.modified_workflow is not None
                ):
                    modified_list.append(path)
                elif (
                    event_type == Change.deleted
                    and watchfolder.deleted_workflow is not None
                ):
                    deleted_list.append(path)

            if len(added_list) > 0:
                # get intitial variables
                variables = dict(watchfolder.added_variables)
                # add files list
                variables[watchfolder.added_items_key] = added_list
                self.workflows.start(
                    watchfolder.added_workflow.id,
                    watchfolder.added_workflow.version,
                    variables,
                )
            if len(modified_list) > 0:
                # get intitial variables
                variables = dict(watchfolder.modified_variables)
                # add files list
                variables[watchfolder.modified_items_key] = modified_list
                self.workflows.start(
                    watchfolder.modified_workflow.id,
                    watchfolder.modified_workflow.version,
                    variables,
                )
            if len(deleted_list) > 0:
                # get intitial variables
                variables = dict(watchfolder.deleted_variables)
                # add files list
                variables[watchfolder.deleted_items_key] = deleted_list
                self.workflows.start(
                    watchfolder.deleted_workflow.id,
                    watchfolder.deleted_workflow.version,
                    variables,
                )

    def stop(self, watchfolder_id: uuid.UUID):
        """
        Stop watchfolder by watchfolder_id

        :param watchfolder_id: Watchfolder ID
        :return:
        """
        # stop watchfolder process
        self.register[watchfolder_id].process.kill()
        self.update(
            self.register[watchfolder_id].watchfolder,
            status=STATUS_STOPPED,
            end_at=datetime.now(),
        )
        del self.register[watchfolder_id]

    def _register_runner_and_start(self, watchfolder: Watchfolder):
        """
        Register and start watchfolder

        :param watchfolder: Watchfolder instance
        :return:
        """
        self.register[watchfolder.id] = WatchfolderRunner(
            watchfolder, Process(target=self.watcher, args=(watchfolder,), daemon=True)
        )

        # start wachfolder in a background process to stop it as we want
        self.register[watchfolder.id].process.start()
