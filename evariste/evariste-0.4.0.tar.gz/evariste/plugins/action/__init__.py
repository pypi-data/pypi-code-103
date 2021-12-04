# Copyright Louis Paternault 2017-2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Actions performed to compile files."""

import io
import logging
import os
import threading

from evariste import errors, plugins
from evariste import hooks

LOGGER = logging.getLogger(__name__)

################################################################################
# Cache log


class CacheLogHook(hooks.ContextHook):
    """Hook called before and after compilation of one file."""

    # pylint: disable=too-few-public-methods

    hookname = "File.compile"

    def __init__(self, plugin, tree):
        super().__init__(plugin)
        self.tree = tree

    def __exit__(self, *args, **kwargs):
        """Store the log in cache."""
        tree = self.tree

        # Saving log into cache
        self.local.tree[tree.from_source] = tree.report.log


class CacheLog(plugins.PluginBase):
    """Cache compilation log."""

    # pylint: disable=too-few-public-methods

    plugin_type = ""
    keyword = "cachelog"
    hooks = [CacheLogHook]


################################################################################
# Actions


class Action(plugins.PluginBase):
    """Generic action"""

    # pylint: disable=too-many-instance-attributes, too-few-public-methods

    plugin_type = "action"
    lock = threading.Lock()

    def compile(self, path):
        """Compile ``path``, catching :class:`EvaristeError` exceptions.

        This function *must* be thread-safe. It can use `self.lock` if
        necessary.
        """
        raise NotImplementedError()

    def match(self, value):
        """Argument `value` is a :class:`Tree` object."""
        # pylint: disable=unused-argument
        return False


class DirectoryAction(Action):
    """Fake action on directories."""

    # pylint: disable=abstract-method, too-few-public-methods

    keyword = "action.directory"

    def compile(self, path):
        success = self._success(path)
        if success:
            message = ""
        else:
            message = "At least one file in this directory failed."
        return Report(path, success=success, log=message, targets=[])

    @staticmethod
    def _success(path):
        """Return ``True`` if compilation of all subpath succeeded."""
        for sub in path:
            if not path[sub].report.success:
                return False
        return True

    def match(self, dummy):
        return False


################################################################################
# Reports


class Report:
    """Report of an action. Mainly a namespace with very few methods."""

    def __init__(self, path, targets=None, success=False, log=None, depends=None):
        # pylint: disable=too-many-arguments

        self.depends = depends
        if self.depends is None:
            self.depends = set()

        if log is None:
            self.log = ""
        else:
            self.log = log

        self.path = path
        if targets is None:
            self.targets = []
        else:
            self.targets = targets
        self._success = success

    @property
    def full_depends(self):
        """Set of files this action depends on, including ``self.path``."""
        return self.depends | set([self.path.from_fs])

    @property
    def success(self):
        """Success getter"""
        return self._success

    @success.setter
    def success(self, value):
        """Success setter."""
        self._success = value
