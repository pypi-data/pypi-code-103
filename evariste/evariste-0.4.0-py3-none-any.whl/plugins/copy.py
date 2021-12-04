# Copyright Louis Paternault 2015-2021
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

"""Plugin to copy files at the end of compilation and rendering."""

import glob

from evariste import plugins, utils
from evariste import hooks


class _Close(hooks.ContextHook):
    """Hook to copy files at the end of compilation."""

    # pylint: disable=too-few-public-methods

    hookname = "Builder.close"

    def __init__(self, plugin, builder):
        # pylint: disable=unused-argument
        super().__init__(plugin)

    def __exit__(self, *args, **kwargs):
        for key in self.local.setup:
            if key.startswith("copy"):
                if isinstance(self.local.setup[key], str):
                    arguments = self.local.setup[key].split()
                else:
                    arguments = self.local.setup[key]
                try:
                    sources, dest = arguments
                except (ValueError, TypeError) as error:
                    raise ValueError(
                        f"""[copy] Option "{key}" should be "SOURCE DEST"."""
                    ) from error
                if dest is None:
                    continue
                for path in glob.iglob(sources):
                    utils.copytree(path, dest)
        return super().__exit__(*args, **kwargs)


class Copy(plugins.PluginBase):
    """Copy files at the end of compilation."""

    # pylint: disable=too-few-public-methods

    plugin_type = ""
    keyword = "copy"
    hooks = [_Close]
