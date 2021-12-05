"""User-defined exceptions."""

from pathlib import Path


class PoetryAliasError(Exception):
    """Base class for ``poetry-alias``-related exceptions."""


class DuplicateAliasError(PoetryAliasError):
    """Raised when trying to add an already existing alias."""

    def __init__(self, alias: str, project_path: Path) -> None:
        self.alias = alias
        self.project_path = project_path
        super().__init__(
            f"Alias `{alias}` already exists for project {project_path}"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"({self.alias!r}, Path('{self.project_path}'))"
        )


class UnknownAliasError(PoetryAliasError):
    """Raised when trying to access or delete a non-existing alias."""

    def __init__(self, alias: str) -> None:
        self.alias = alias
        super().__init__(f"Alias `{alias}` does not exist")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.alias!r})"
