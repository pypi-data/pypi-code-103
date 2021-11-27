# Copyright 2020 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests"""

import glob
import importlib
import os
import unittest

import spix


class TestParse(unittest.TestCase):
    """Test that command lines are correctly parsed from .tex files."""

    DATADIR = os.path.join(os.path.dirname(__file__), "parsedata")

    def _iter_data(self):
        """Iterate over test data: a source .tex file, and the expected snippets."""
        for texname in glob.glob(os.path.join(self.DATADIR, "*.tex")):
            name = os.path.basename(texname)[:-4]

            with open(
                os.path.join(self.DATADIR, f"{name}.tex"), encoding="utf8"
            ) as texfile:
                yield (
                    name,
                    texfile.readlines(),
                    importlib.import_module(
                        f".parsedata.{name}", package="test"
                    ).snippets,
                )

    def test_parse(self):
        """Test that snippets in tex files are correctly extracted."""
        for name, tex, snippets in self._iter_data():
            with self.subTest(name):
                self.assertListEqual(
                    list(spix.parse_lines(tex)),
                    snippets,
                )
