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

from difflib import unified_diff
from pathlib import Path
from typing import Optional

from .discovery import TestDefinition, Variables
from .exception import AssertError
from .template import AnsibleTemplateRenderer


class Test:
    _role_path: Path
    _test_definition_src_path: Path
    _test_definition: TestDefinition
    _renderer: AnsibleTemplateRenderer

    def __init__(self, role_path: Path, src_path: Path,
                 testdef: TestDefinition):
        self._role_path = role_path
        self._test_definition_src_path = src_path
        self._test_definition = testdef
        self._renderer = AnsibleTemplateRenderer(self._role_path)

    @property
    def _base_path(self) -> Path:
        parent_path = self._test_definition_src_path.parent
        if parent_path.is_absolute():
            return parent_path
        return self._role_path.joinpath("templates_tests", parent_path)

    @property
    def _inventory_path(self) -> Optional[Path]:
        if not self._test_definition.has_inventory():
            return None
        assert isinstance(self._test_definition.variables, Variables)
        assert isinstance(self._test_definition.variables.inventory, Path)
        return self._base_path.joinpath(
            self._test_definition.variables.inventory,
        )

    @property
    def _extra_path(self) -> Optional[Path]:
        if not self._test_definition.has_extra():
            return None
        assert isinstance(self._test_definition.variables, Variables)
        assert isinstance(self._test_definition.variables.extra, Path)
        return self._base_path.joinpath(self._test_definition.variables.extra)

    def run(self) -> None:
        actual = self._renderer.render(
            template=self._test_definition.template,
            inventory=self._inventory_path,
            extra=self._extra_path,
        )

        expect_path = self._base_path.joinpath(
            self._test_definition.expected_result,
        )
        expect = expect_path.read_text()

        fromfile_path = expect_path.relative_to(self._role_path)
        tofile_path = Path("templates", self._test_definition.template)
        diff = "\n".join(
            unified_diff(
                a=expect.splitlines(),
                b=actual.splitlines(),
                fromfile=str(fromfile_path),
                tofile=f"render({tofile_path})",
                lineterm="",
            ),
        )
        if diff:
            raise AssertError(diff)
