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

from pathlib import Path
from typing import Any, Iterator, NamedTuple, Optional, Tuple

from packaging.version import InvalidVersion, Version
from yaml import safe_load, YAMLError

from .exception import TestDefinitionError


SUPPORTED_SPEC_VERSION = "0.1"


class Meta(NamedTuple):
    version: Version

    @classmethod
    def load(cls, base_path: Path = Path("templates_tests")) -> "Meta":
        document = cls._load_document(base_path)

        if not isinstance(document, dict):
            raise TestDefinitionError("meta is not a dictionary")

        try:
            version_string = document["version"]
        except KeyError as exc:
            msg = "testing speification version is not specified"
            raise TestDefinitionError(msg) from exc

        try:
            version = Version(version_string)
        except (InvalidVersion, TypeError) as exc:
            msg = "invalid testing speification version"
            raise TestDefinitionError(msg) from exc

        return cls(version)

    @staticmethod
    def _load_document(base_path: Path) -> Any:
        data_path = Path(base_path, "meta.yml")

        try:
            data = data_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise TestDefinitionError("meta is not defined") from exc

        try:
            document = safe_load(data)
        except YAMLError as exc:
            raise TestDefinitionError("meta is badly formatted") from exc

        return document


class Variables(NamedTuple):
    inventory: Optional[Path]
    extra: Optional[Path]

    @classmethod
    def create(cls, document: Any) -> "Variables":
        if not isinstance(document, dict):
            msg = "variables attribute is not a dictionary"
            raise TestDefinitionError(msg)

        inventory: Optional[Path] = None
        extra: Optional[Path] = None

        for key, value in document.items():
            if not isinstance(key, str):
                msg = "key is not a string"
                raise TestDefinitionError(msg)
            if key == "inventory":
                if value is not None:
                    try:
                        inventory = _create_path(value)
                    except TestDefinitionError as exc:
                        msg = "invalid inventory attribute"
                        raise TestDefinitionError(msg) from exc
            elif key == "extra":
                if value is not None:
                    try:
                        extra = _create_path(value)
                    except TestDefinitionError as exc:
                        msg = "invalid extra attribute"
                        raise TestDefinitionError(msg) from exc
            else:
                msg = f"unknown attribute: {key}"
                raise TestDefinitionError(msg)

        return cls(inventory, extra)


class TestDefinition(NamedTuple):
    name: str
    template: Path
    variables: Optional[Variables]
    expected_result: Path

    def has_inventory(self) -> bool:
        if self.variables is None or self.variables.inventory is None:
            return False
        return True

    def has_extra(self) -> bool:
        if self.variables is None or self.variables.extra is None:
            return False
        return True

    @classmethod
    def create(cls, document: Any) -> "TestDefinition":
        # pylint: disable=too-many-branches
        if not isinstance(document, dict):
            msg = "test definition is not a dictionary"
            raise TestDefinitionError(msg)

        name: Optional[str] = None
        template: Optional[Path] = None
        variables: Optional[Variables] = None
        expected_result: Optional[Path] = None

        for key, value in document.items():
            if not isinstance(key, str):
                msg = "key is not a string"
                raise TestDefinitionError(msg)
            if key == "name":
                if value is not None:
                    if not isinstance(value, str):
                        raise TestDefinitionError("name is not a string")
                    name = value
            elif key == "template":
                if value is not None:
                    try:
                        template = _create_path(value)
                    except TestDefinitionError as exc:
                        msg = "invalid template attribute"
                        raise TestDefinitionError(msg) from exc
            elif key == "variables":
                if value is not None:
                    try:
                        variables = Variables.create(value)
                    except TestDefinitionError as exc:
                        msg = "invalid variables attribute"
                        raise TestDefinitionError(msg) from exc
            elif key == "expected_result":
                if value is not None:
                    try:
                        expected_result = _create_path(value)
                    except TestDefinitionError as exc:
                        msg = "invalid expected result attribute"
                        raise TestDefinitionError(msg) from exc
            else:
                msg = f"unknown attribute: {key}"
                raise TestDefinitionError(msg)

        if name is None:
            msg = "name is not specified"
            raise TestDefinitionError(msg)
        if template is None:
            msg = "template is not specified"
            raise TestDefinitionError(msg)
        if expected_result is None:
            msg = "expected result is not specified"
            raise TestDefinitionError(msg)

        return cls(name, template, variables, expected_result)


def _create_path(document: Any) -> Path:
    if not isinstance(document, str):
        raise TestDefinitionError("path is not a string")
    if len(document) == 0:
        raise TestDefinitionError("path is empty string")
    path = Path(document)
    if path.is_absolute():
        raise TestDefinitionError("path is not relative")
    return path


def _iter_testdefs(document: Any) -> Iterator[TestDefinition]:
    if not isinstance(document, dict):
        msg = "test definitions document is not a dictionary"
        raise TestDefinitionError(msg)

    tests_defined = False
    for key, value in document.items():
        if not isinstance(key, str):
            msg = "key is not a string"
            raise TestDefinitionError(msg)
        if key == "tests":
            tests_defined = True
            if value is not None:
                if not isinstance(value, list):
                    msg = "test definitions are not list"
                    raise TestDefinitionError(msg)
                for testdef_idx, testdef_doc in enumerate(value):
                    try:
                        testdef = TestDefinition.create(testdef_doc)
                    except TestDefinitionError as exc:
                        msg = f"invalid test definition #{testdef_idx}"
                        raise TestDefinitionError(msg) from exc
                    yield testdef
        else:
            msg = f"unknown attribute: {key}"
            raise TestDefinitionError(msg)
    if not tests_defined:
        msg = "test definitions are not specified"
        raise TestDefinitionError(msg)


def _find(base_path: Path, pattern: str) -> Iterator[Path]:
    for path in base_path.glob(pattern):
        yield path.relative_to(base_path)


def discover_tests(base_path: Path = Path("templates_tests")) \
        -> Iterator[Tuple[TestDefinition, Path]]:
    try:
        meta = Meta.load(base_path)
    except TestDefinitionError as exc:
        msg = "failed to get tests metadata"
        raise TestDefinitionError(msg) from exc

    if meta.version != Version(SUPPORTED_SPEC_VERSION):
        msg = "unsupported testing speification version"
        raise TestDefinitionError(msg)

    for path in _find(base_path, "**/test*.yml"):
        data = base_path.joinpath(path).read_text(encoding="utf-8")
        try:
            document = safe_load(data)
        except YAMLError as exc:
            msg = f"test definition file '{path}' is badly formatted"
            raise TestDefinitionError(msg) from exc

        try:
            for testdef in _iter_testdefs(document):
                yield (testdef, path)
        except TestDefinitionError as exc:
            msg = f"invalid definition file '{path}'"
            raise TestDefinitionError(msg) from exc
