"""Tests for the :mod:`poetry_alias.commands` module."""

import re
from pathlib import Path
from typing import Callable, Generator, Type
from unittest.mock import patch

import pytest
from cleo.application import Application
from cleo.exceptions import MissingArgumentsException, ValueException
from cleo.testers.command_tester import CommandTester
from poetry.console.commands.command import Command

from .conftest import aliases_data
from ..commands import (
    AddCommand,
    AliasCommand,
    CleanCommand,
    ListCommand,
    PruneCommand,
    RemoveCommand,
    ShowCommand,
)


@pytest.fixture
def command_tester(aliases_path: Path) -> Generator[Callable, None, None]:
    """Return a callable for creating :class:`CommandTester` instances."""
    with patch.object(AliasCommand, "aliases_path", aliases_path):

        def _create_tester(command_class: Type[Command]) -> CommandTester:
            """Create a :class:`CommandTester` for the passed command class."""
            application = Application()
            application.add(command_class())
            command = application.find(command_class.name)
            tester = CommandTester(command)
            return tester

        yield _create_tester


@pytest.mark.parametrize(
    "command, expected_name",
    [
        (AddCommand, "alias add"),
        (CleanCommand, "alias clean"),
        (ListCommand, "alias list"),
        (PruneCommand, "alias prune"),
        (RemoveCommand, "alias rm"),
        (ShowCommand, "alias show"),
    ],
)
def test_command_name(command: Command, expected_name: str) -> None:
    """Test a command’s name."""
    assert command.name == expected_name


def test_add_without_name(command_tester: Callable) -> None:
    """Verify that ``add`` without a name raises an exception."""
    tester = command_tester(AddCommand)
    with pytest.raises(MissingArgumentsException):
        tester.execute()


def test_add(command_tester: Callable) -> None:
    """Test adding a new alias."""
    add_tester = command_tester(AddCommand)
    show_tester = command_tester(ShowCommand)
    with patch.object(AliasCommand, "project_path", aliases_data["ham"]):
        add_tester.execute("fnord")
        show_tester.execute()
    output = show_tester.io.fetch_output()
    assert output == "eggs\nfnord\nham\n"


def test_clean(command_tester: Callable) -> None:
    """Verify that no aliases are listed after running ``clean``."""
    clean_tester = command_tester(CleanCommand)
    clean_tester.execute()
    clean_output = clean_tester.io.fetch_output()
    expected = "Removed aliases\n" + "".join(
        sorted(
            f"{alias}: {project_path}\n"
            for alias, project_path in aliases_data.items()
        )
    )
    assert clean_output == expected
    list_tester = command_tester(ListCommand)
    list_tester.execute()
    list_output = list_tester.io.fetch_output()
    assert list_output == ""

    # Calling “clean” again removes no further aliases
    clean_tester.execute()
    clean_output = clean_tester.io.fetch_output()
    assert clean_output == "No aliases removed\n"


def test_list_prints_all_aliases(command_tester: Callable) -> None:
    """Verify that ``list`` prints all aliases in alphabetical order."""
    tester = command_tester(ListCommand)
    tester.execute()
    output = tester.io.fetch_output()
    expected = "".join(
        sorted(
            f"{alias}: {project_path}\n"
            for alias, project_path in aliases_data.items()
        )
    )
    assert output == expected


def test_prune_command(command_tester: Callable) -> None:
    """Test the ``prune`` command."""
    tester = command_tester(PruneCommand)
    tester.execute()
    output = tester.io.fetch_output()
    expected = "Removed aliases\n" + "".join(
        sorted(
            f"{alias}: {project_path}\n"
            for alias, project_path in aliases_data.items()
        )
    )
    assert output == expected

    # Calling “prune” again removes no further aliases
    tester.execute()
    output = tester.io.fetch_output()
    assert output == "No dangling aliases found\n"


def test_remove_alias(command_tester: Callable) -> None:
    """Verify that a removed alias does not get listed."""
    alias = "ham"
    rm_tester = command_tester(RemoveCommand)
    rm_tester.execute(alias)
    list_tester = command_tester(ListCommand)
    list_tester.execute()
    list_output = list_tester.io.fetch_output()
    assert re.search(f"^{alias}: ", list_output, re.MULTILINE) is None


def test_remove_all_project_aliases(command_tester: Callable) -> None:
    """Verify that ``rm`` without arguments remove all project aliases."""
    rm_tester = command_tester(RemoveCommand)
    show_tester = command_tester(ShowCommand)
    with patch.object(AliasCommand, "project_path", aliases_data["ham"]):
        rm_tester.execute()
        show_tester.execute()
    output = show_tester.io.fetch_output()
    assert output == ""


def test_remove_unknown_alias(command_tester: Callable) -> None:
    """Verify that removing an unknown alias raises an exception."""
    rm_tester = command_tester(RemoveCommand)
    with pytest.raises(ValueException):
        rm_tester.execute("fnord")


def test_show_alias(command_tester: Callable) -> None:
    """Test the ``show`` command."""
    tester = command_tester(ShowCommand)
    with patch.object(AliasCommand, "project_path", aliases_data["ham"]):
        tester.execute()
        output = tester.io.fetch_output()
    assert output == "eggs\nham\n"
