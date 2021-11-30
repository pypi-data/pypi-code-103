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
from twisted.python.procutils import which
from sat.core.log import getLogger
from sat.tools.common import async_process
from sat.core import exceptions
from sat.core.i18n import _
from typing import Optional

log = getLogger(__name__)


class Task:
    """Handle tasks of a Libervia site"""
    # can be "stop" or "continue"
    ON_ERROR: str = "stop"
    LOG_OUTPUT: bool = True
    # list of directories to check for restarting this task
    # Task.onDirEvent will be called if it exists, otherwise
    # the task will be run and Task.start will be called
    WATCH_DIRS: Optional[list] = None
    # list of task names which must be prepared/started before this one
    AFTER: Optional[list] = None

    def __init__(self, manager, task_name):
        self.manager = manager
        self.name = task_name

    @property
    def host(self):
        return self.manager.host

    @property
    def resource(self):
        return self.manager.resource

    @property
    def site_path(self):
        return self.manager.site_path

    @property
    def build_path(self):
        """path where generated files will be build for this site"""
        return self.manager.build_path

    def getConfig(self, key, default=None, value_type=None):
        return self.host.getConfig(self.resource, key=key, default=default,
                                   value_type=value_type)

    @property
    def site_name(self):
        return self.resource.site_name

    def findCommand(self, name, *args):
        """Find full path of a shell command

        @param name(unicode): name of the command to find
        @param *args(unicode): extra names the command may have
        @return (unicode): full path of the command
        @raise exceptions.NotFound: can't find this command
        """
        names = (name,) + args
        for n in names:
            try:
                cmd_path = which(n)[0]
            except IndexError:
                pass
            else:
                return cmd_path
        raise exceptions.NotFound(_(
            "Can't find {name} command, did you install it?").format(name=name))

    def runCommand(self, command, *args, **kwargs):
        kwargs['verbose'] = self.LOG_OUTPUT
        return async_process.CommandProtocol.run(command, *args, **kwargs)
