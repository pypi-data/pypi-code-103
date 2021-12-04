# Copyright Louis Paternault 2015-2020
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

"""Abstract utilities for file renderers using Jinja2."""

from evariste.plugins.renderer import FileRenderer


class Jinja2FileRenderer(FileRenderer):
    """Renderer of file using jinja2"""

    keyword = None
    extension = None
    priority = -float("inf")
    template = "default"

    def match(self, filename):
        """This is the default renderer, that matches everything."""
        # pylint: disable=unused-argument
        return True

    def render(self, filename, context):
        """Render ``tree``, which is a :class:`tree.File`."""
        # pylint: disable=arguments-differ
        return context[f"file_{self.template}"](filename)
