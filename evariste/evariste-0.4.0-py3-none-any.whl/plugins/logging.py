# Copyright Louis Paternault 2021
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

"""Plugin log progress."""

import logging
import threading

from evariste import hooks
from evariste import plugins


class CompileTree(hooks.ContextHook):
    """Hook called before and after compilation of all files."""

    # pylint: disable=too-few-public-methods

    hookname = "Builder.compile"

    def __init__(self, plugin, builder):
        super().__init__(plugin)
        plugin.total = builder.tree.count()


class CompileFile(hooks.ContextHook):
    """Hook called before and after compilation of one file."""

    # pylint: disable=too-few-public-methods

    hookname = "File.compile"

    def __init__(self, plugin, tree):
        super().__init__(plugin)
        self.tree = tree
        self.logger = logging.getLogger("evariste.tree")
        with plugin.lock:
            plugin.count += 1
            self.count = plugin.count

    def __enter__(self, *args, **kwargs):
        self.logger.info(
            f"Compiling [{self.count: >{len(str(self.plugin.total))}}/{self.plugin.total}] "
            f"'{self.tree.from_source}'…"
        )
        super().__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        if self.tree.report.success:
            self.logger.info(
                f"Compiling [{self.count: >{len(str(self.plugin.total))}}/{self.plugin.total}] "
                f"'{self.tree.from_source}': success."
            )
        else:
            self.logger.info(
                f"Compiling [{self.count: >{len(str(self.plugin.total))}}/{self.plugin.total}] "
                f"'{self.tree.from_source}': failed."
            )
        super().__exit__(*args, **kwargs)


class Logging(plugins.PluginBase):
    """Log stuff"""

    # pylint: disable=too-few-public-methods

    plugin_type = ""
    keyword = "logging"
    hooks = [CompileFile, CompileTree]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = threading.Lock()
        self.count = 0
        self.total = 0
