#!/usr/bin/env python3

# Libervia: a Salut à Toi frontend
# Copyright (C) 2011-2021 Jérôme Poisson <goffi@goffi.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import os.path
from pathlib import Path
from typing import Dict
import importlib.util
from twisted.internet import defer
from sat.core.log import getLogger
from sat.core import exceptions
from sat.core.i18n import _
from sat.tools import utils
from libervia.server.constants import Const as C
from . import implicit
from .task import Task

log = getLogger(__name__)

DEFAULT_SITE_LABEL = _("default site")


class TasksManager:
    """Handle tasks of a Libervia site"""

    def __init__(self, host, site_resource):
        """
        @param site_resource(LiberviaRootResource): root resource of the site to manage
        """
        self.host = host
        self.resource = site_resource
        self.tasks_dir = self.site_path / C.TASKS_DIR
        self.tasks = {}
        self._build_path = None
        self._current_task = None

    @property
    def site_path(self):
        return Path(self.resource.site_path)

    @property
    def build_path(self):
        """path where generated files will be build for this site"""
        if self._build_path is None:
            self._build_path = self.host.getBuildPath(self.site_name)
        return self._build_path

    @property
    def site_name(self):
        return self.resource.site_name

    def validateData(self, task):
        """Check workflow attributes in task"""

        for var, allowed in (("ON_ERROR", ("continue", "stop")),
                             ("LOG_OUTPUT", bool),
                             ("WATCH_DIRS", list)):
            value = getattr(task, var)

            if isinstance(allowed, type):
                if allowed is list and value is None:
                    continue
                if not isinstance(value, allowed):
                    raise ValueError(
                        _("Unexpected value for {var}, {allowed} is expected.")
                        .format(var=var, allowed=allowed))
            else:
                if not value in allowed:
                    raise ValueError(_("Unexpected value for {var}: {value!r}").format(
                        var=var, value=value))

    async def importTask(
        self,
        task_name: str,
        task_path: Path,
        to_import: Dict[str, Path]
    ) -> None:
        if task_name in self.tasks:
            log.debug(f"skipping task {task_name} which is already imported")
            return
        module_name = f"{self.site_name or C.SITE_NAME_DEFAULT}.task.{task_name}"

        spec = importlib.util.spec_from_file_location(module_name, task_path)
        task_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_module)
        task = task_module.Task(self, task_name)
        if task.AFTER is not None:
            for pre_task_name in task.AFTER:
                log.debug(
                    f"task {task_name!r} must be run after {pre_task_name!r}")
                try:
                    pre_task_path = to_import[pre_task_name]
                except KeyError:
                    raise ValueError(
                        f"task {task_name!r} must be run after {pre_task_name!r}, "
                        f"however there is no task with such name")
                await self.importTask(pre_task_name, pre_task_path, to_import)

        # we launch prepare, which is a method used to prepare
        # data at runtime (e.g. set WATCH_DIRS using config)
        try:
            prepare = task.prepare
        except AttributeError:
            pass
        else:
            log.info(_('== preparing task "{task_name}" for {site_name} =='.format(
                task_name=task_name, site_name=self.site_name or DEFAULT_SITE_LABEL)))
            try:
                await utils.asDeferred(prepare)
            except exceptions.CancelError as e:
                log.debug(f"Skipping {task_name} which cancelled itself: {e}")
                return

        self.tasks[task_name] = task
        self.validateData(task)
        if self.host.options['dev-mode']:
            dirs = task.WATCH_DIRS or []
            for dir_ in dirs:
                self.host.files_watcher.watchDir(
                    dir_, auto_add=True, recursive=True,
                    callback=self._autorunTask, task_name=task_name)

    async def parseTasksDir(self, dir_path: Path) -> None:
        log.debug(f"parsing tasks in {dir_path}")
        tasks_paths = sorted(dir_path.glob('task_*.py'))
        to_import = {}
        for task_path in tasks_paths:
            if not task_path.is_file():
                continue
            task_name = task_path.stem[5:].lower().strip()
            if not task_name:
                continue
            if task_name in self.tasks:
                raise exceptions.ConflictError(
                    "A task with the name [{name}] already exists".format(
                        name=task_name))
            log.debug(f"task {task_name} found")
            to_import[task_name] = task_path

        for task_name, task_path in to_import.items():
            await self.importTask(task_name, task_path, to_import)

    async def parseTasks(self):
        # implicit tasks are always run
        implicit_path = Path(implicit.__file__).parent
        await self.parseTasksDir(implicit_path)
        # now we check if there are tasks specific to this site
        if not self.tasks_dir.is_dir():
            log.debug(_("{name} has no task to launch.").format(
                name = self.resource.site_name or DEFAULT_SITE_LABEL))
            return
        else:
            await self.parseTasksDir(self.tasks_dir)

    def _autorunTask(self, host, filepath, flags, task_name):
        """Called when an event is received from a watched directory"""
        if flags == ['create']:
            return
        try:
            task = self.tasks[task_name]
            on_dir_event_cb = task.onDirEvent
        except AttributeError:
            return defer.ensureDeferred(self.runTask(task_name))
        else:
            return utils.asDeferred(
                on_dir_event_cb, host, Path(filepath.path.decode()), flags)

    async def runTaskInstance(self, task: Task) -> None:
        self._current_task = task.name
        log.info(_('== running task "{task_name}" for {site_name} =='.format(
            task_name=task.name, site_name=self.site_name or DEFAULT_SITE_LABEL)))
        os.chdir(self.site_path)
        try:
            await utils.asDeferred(task.start)
        except Exception as e:
            on_error = task.ON_ERROR
            if on_error == 'stop':
                raise e
            elif on_error == 'continue':
                log.warning(_('Task "{task_name}" failed for {site_name}: {reason}')
                    .format(task_name=task.name, site_name=self.site_name, reason=e))
            else:
                raise exceptions.InternalError("we should never reach this point")
        self._current_task = None

    async def runTask(self, task_name: str) -> None:
        """Run a single task

        @param task_name(unicode): name of the task to run
        """
        task = self.tasks[task_name]
        await self.runTaskInstance(task)

    async def runTasks(self):
        """Run all the tasks found"""
        old_path = os.getcwd()
        for task_name, task_value in self.tasks.items():
            await self.runTask(task_name)
        os.chdir(old_path)
