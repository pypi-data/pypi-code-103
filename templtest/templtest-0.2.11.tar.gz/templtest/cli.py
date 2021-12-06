# templtest -- a tool for testing Ansible role templates
# Copyright (C) 2021  Alexey Busygin
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from argparse import ArgumentParser, Namespace
from pathlib import Path
from sys import exit
from typing import List, Optional

from .discovery import discover_tests
from .exception import AssertError, TestDefinitionError
from .test import Test


def _parse_args(args: Optional[List[str]] = None) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--role-path", type=Path, default=Path("."))
    return parser.parse_args(args)


def main(argv: Optional[List[str]] = None) -> None:
    args = _parse_args(argv)
    tests_path = Path(args.role_path, "templates_tests")
    if tests_path.is_dir():
        try:
            for testdef, src_path in discover_tests(tests_path):
                test = Test(args.role_path, src_path, testdef)
                print(f"[{src_path}] {testdef.name} ... ", end="")
                try:
                    test.run()
                except AssertError as exc:
                    print("fail")
                    print(exc.args[0])
                    exit(1)
                else:
                    print("ok")
        except TestDefinitionError as exc:
            exception: Optional[BaseException] = exc
            print("TestDefinitionError", end="")
            while exception is not None:
                print(f": {exception.args[0]}", end="")
                exception = exception.__cause__
            exit(1)
