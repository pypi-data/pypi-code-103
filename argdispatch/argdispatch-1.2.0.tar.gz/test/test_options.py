# Copyright 2016-2021 Louis Paternault
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

"""Test of various options"""

import sys

import argdispatch

from . import TestArgparse
from . import binpath, pythonpath


def function_foo(args):
    """This is the docstring of function foo."""
    # pylint: disable=consider-using-f-string
    print("Running function_foo({})".format(", ".join(args)))
    sys.exit(1)


class TestOndouble(TestArgparse):
    """Test of the ``ondouble`` argument."""

    @pythonpath("pythonpath1")
    @binpath("binpath1")
    def test_ignore(self):
        """Test of ``ondouble=IGNORE``."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_foo, "foo")
        sub.add_function(function_foo, "foo", ondouble=argdispatch.IGNORE)
        sub.add_module("foo", ondouble=argdispatch.IGNORE)
        sub.add_executable("bin11", "foo", ondouble=argdispatch.IGNORE)

        with self.assertStdoutMatches(r"^\s*foo\s", count=1):
            with self.assertExit(0):
                parser.parse_args("--help".split())

    @pythonpath("pythonpath1")
    @binpath("binpath1")
    def test_error(self):
        """Test of ``ondouble=ERROR``."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_foo, "foo")
        with self.assertRaises(ValueError):
            sub.add_function(function_foo, "foo", ondouble=argdispatch.ERROR)
        with self.assertRaises(ValueError):
            sub.add_module("foo", ondouble=argdispatch.ERROR)
        with self.assertRaises(ValueError):
            sub.add_executable("bin11", "foo", ondouble=argdispatch.ERROR)

    def test_add_parser(self):
        """Test of ``ondouble`` argument with the ``add_parser`` method."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_foo, "foo")
        with self.subTest():
            with self.assertRaises(ValueError):
                sub.add_parser("foo", ondouble=argdispatch.ERROR)
        with self.subTest():
            sub.add_parser("foo", ondouble=argdispatch.IGNORE)
            with self.assertStdoutMatches(r"^\s*foo", count=1):
                with self.assertExit(0):
                    parser.parse_args("--help".split())

    @pythonpath("pythonpath1")
    @binpath("binpath1")
    def test_double(self):
        """Test of ``ondouble=DOUBLE``."""
        parser = argdispatch.ArgumentParser()
        sub = parser.add_subparsers()
        sub.add_function(function_foo, "foo")
        sub.add_function(function_foo, "foo", ondouble=argdispatch.DOUBLE)
        sub.add_module("foo", ondouble=argdispatch.DOUBLE)
        sub.add_executable("bin11", "foo", ondouble=argdispatch.DOUBLE)
        with self.assertStdoutMatches(r"^\s*foo", count=4):
            with self.assertExit(0):
                parser.parse_args("--help".split())
