"""Handlers for the `alias` CLI commands."""

from abc import ABC
from os import chdir, environ
from pathlib import Path
from typing import Optional

from cleo.exceptions import ValueException
from cleo.helpers import argument
from poetry.console.commands.command import Command
from poetry.locations import CACHE_DIR

from .exceptions import UnknownAliasError
from .manager import AliasManager


class AliasCommand(Command, ABC):
    """Base class for `alias` CLI command handlers."""

    aliases_path: Path = Path(CACHE_DIR) / "virtualenvs" / "aliases.toml"
    _manager: Optional[AliasManager] = None

    @property
    def manager(self) -> AliasManager:
        """Return the internal :class:`AliasManager` instance."""
        if not self._manager:
            self._manager = AliasManager(self.aliases_path)
        return self._manager

    @property
    def project_path(self) -> Path:
        """Return the path to the current project."""
        return self.poetry.file.parent


class AddCommand(AliasCommand):
    """Handler class for the ``poetry alias add`` command."""

    name = "alias add"
    description = "Add an alias for the current project."
    arguments = [argument("name", "The alias to set for the current project.")]

    def handle(self) -> None:
        """Add a new project alias."""
        name = self.argument("name")
        self.manager.add(name, self.project_path)


class CleanCommand(AliasCommand):
    """Handler class for the ``poetry alias clean`` command."""

    name = "alias clean"
    description = "Remove all alias definitions."

    def handle(self) -> None:
        """Remove all alias definitions."""
        removed_aliases = self.manager.clean()
        if not removed_aliases:
            self.line("No aliases removed")
            return
        self.line("<b>Removed aliases</b>")
        for name in sorted(removed_aliases):
            self.line(f"<info>{name}</info>: {removed_aliases[name]}")


class GoCommand(AliasCommand):
    """Handler class for the ``poetry alias go`` command."""

    name = "alias go"
    description = "Change to a project directory and activate its virtualenv."
    arguments = [argument("alias", "The alias of the project to switch to.")]

    def handle(self) -> int:
        """Change to a project directory."""
        # Don't do anything if we are already inside a virtualenv
        active_venv = environ.get("VIRTUAL_ENV", None)
        if active_venv is not None:
            self.line(
                f"Virtual environment already activated: "
                f"<info>{active_venv}</info>.\n"
                f"Please deactivate the current virtual environment first."
            )
            return 2

        alias = self.argument("alias")
        try:
            project_path = self.manager.get_project(alias)
        except UnknownAliasError:
            self.line(f"Alias <info>{alias}</info> does not exist")
            return 2

        # Change directory and activate the virtualenv
        chdir(project_path)
        environ["PWD"] = str(project_path)
        self.call("shell")
        return 0


class ListCommand(AliasCommand):
    """Handler class for the ``poetry alias list`` command."""

    name = "alias list"
    description = "List all project alias definitions."

    def handle(self) -> None:
        """Print a list of all defined aliases."""
        aliases = self.manager.list()
        for name in aliases:
            self.line(f"<info>{name}</info>: {aliases[name]}")


class PruneCommand(AliasCommand):
    """Handler class for the ``poetry alias prune`` command."""

    name = "alias prune"
    description = "Remove aliases that no longer point to a project directory."

    def handle(self) -> None:
        """Remove and print dangling aliases."""
        removed_aliases = self.manager.prune()
        if not removed_aliases:
            self.line("No dangling aliases found")
            return
        self.line("<b>Removed aliases</b>")
        for name in sorted(removed_aliases):
            self.line(f"<info>{name}</info>: {removed_aliases[name]}")


class RemoveCommand(AliasCommand):
    """Handler class for the ``poetry alias remove`` command."""

    name = "alias rm"
    description = "Remove a project alias."
    arguments = [
        argument(
            "name",
            "The alias to remove.  "
            "If omitted, remove all aliases for the current project.",
            optional=True,
        ),
    ]

    def handle(self) -> int:
        """Remove a project alias."""
        name = self.argument("name")
        if name:
            try:
                self.manager.remove_alias(name)
            except UnknownAliasError:
                raise ValueException(f"Alias {name} does not exist")
        else:
            self.manager.remove_project(self.project_path)
        return 0


class ShowCommand(AliasCommand):
    """Handler class for the ``poetry alias show`` command."""

    name = "alias show"
    description = "Show all aliases for the current project."

    def handle(self) -> None:
        """Print a list of all aliases for the current project."""
        for alias in self.manager.get_aliases(self.project_path):
            self.line(alias)
