"""Manage project alias definitions and their persistance to disk."""

from pathlib import Path
from typing import Dict, List

import tomlkit
from poetry.core.toml.file import TOMLFile

from .exceptions import DuplicateAliasError, UnknownAliasError


class AliasManager:
    """Manage project alias definitions."""

    def __init__(self, aliases_path: Path) -> None:
        self.aliases_path = aliases_path
        self.alias_store = AliasStore(aliases_path)
        self.aliases = self.alias_store.load()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(Path({str(self.aliases_path)!r}))"

    def add(self, alias: str, project_path: Path) -> None:
        """Add a project alias.

        :param alias: the alias to add.
        :param project_path: the project directory to add the alias for.
        """
        # Only add the alias if it isn’t already used
        existing_project = self.aliases.get(alias, None)
        if existing_project is None:
            self.aliases[alias] = project_path
            self.save()
            return

        # Raise an exception if the alias already exists for another project
        if existing_project != project_path:
            raise DuplicateAliasError(alias, existing_project)

    def clean(self) -> Dict[str, Path]:
        """Remove all alias definitions.

        :return: all removed aliases, as a mapping of alias names to
                 project directory paths.
        """
        removed_aliases = self.aliases
        self.aliases = {}
        self.save()
        return removed_aliases

    def get_aliases(self, project_path: Path) -> List[str]:
        """Return all defined aliases for a project.

        :param project_path: the project directory to return the aliases for.
        :return: an alphabetically sorted list of all defined aliases
                 for the given project.
        """
        aliases = [a for a in self.aliases if self.aliases[a] == project_path]
        return list(sorted(aliases))

    def get_project(self, alias: str) -> Path:
        """Get the project path for a given alias.

        :param alias: the alias to get the project path for.
        :return: the path to the project associated with the given alias.
        """
        try:
            return self.aliases[alias]
        except KeyError:
            raise UnknownAliasError(alias)

    def list(self) -> Dict[str, Path]:
        """Return all defined project aliases.

        :return: all defined aliases, as a mapping of alias names to
                 project directory paths.
        """
        return self.aliases.copy()

    def prune(self) -> Dict[str, Path]:
        """Remove aliases that no longer point to a project directory.

        :return: a dictionary of all removed aliases, as a mapping of
                 alias names to project directory paths.
        """
        removed_aliases = {}
        for name, project_path in list(self.aliases.items()):
            poetry_file = project_path / "pyproject.toml"
            if not poetry_file.exists():
                del self.aliases[name]
                removed_aliases[name] = project_path
        self.save()
        return removed_aliases

    def remove_alias(self, alias: str) -> None:
        """Remove a project alias.

        :param alias: the alias to remove.
        """
        try:
            del self.aliases[alias]
        except KeyError:
            raise UnknownAliasError(alias)
        self.save()

    def remove_project(self, project_path: Path) -> None:
        """Remove all aliases for a project.

        :param project_path: the project directory to remove the aliases for.
        """
        for alias in self.get_aliases(project_path):
            del self.aliases[alias]
        self.save()

    def save(self) -> None:
        """Persist the currently defined aliases to disk."""
        self.alias_store.save(self.aliases)


class AliasStore:
    """Load and store alias definitions to/from disk."""

    def __init__(self, path: Path) -> None:
        self.aliases_path = path
        self.aliases_file = TOMLFile(path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(Path({str(self.aliases_path)!r}))"

    def load(self) -> Dict[str, Path]:
        """Load alias definitions from a TOML file, and return as dict.

        :return: a mapping of alias names to project directory paths.
        """
        aliases = {}
        for dirname, dirdata in self.aliases_file.read().items():
            for alias in dirdata["aliases"]:
                aliases[alias] = Path(dirname)
        return aliases

    def save(self, aliases: Dict[str, Path]) -> None:
        """Store a dict with aliases definitions to a TOML file on disk.

        :param aliases: a mapping of alias names to project directory
                        paths which shall be persisted.
        """
        projects: Dict[Path, List[str]] = {}
        for alias, project_path in sorted(aliases.items()):
            projects.setdefault(project_path, []).append(alias)
        doc = tomlkit.document()
        for project_path in sorted(projects):
            table = tomlkit.table()
            project_aliases = sorted(projects[project_path])
            table.add("aliases", project_aliases)
            doc.add(str(project_path), table)
        self.aliases_file.write(doc)
