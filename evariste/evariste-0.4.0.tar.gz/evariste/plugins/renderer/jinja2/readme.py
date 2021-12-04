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

"""Common utilities for readme renderers using Jinja2"""

from evariste.plugins.renderer import ReadmeRenderer


class Jinja2ReadmeRenderer(ReadmeRenderer):
    """Abstract class for readme renderers using jinja2."""

    # pylint: disable=too-few-public-methods, abstract-method

    extensions = []

    def render(self, path, context):
        """Render README."""
        # pylint: disable=unused-argument
        with open(path, encoding="utf8") as source:
            return source.read()
