"""Fixtures for tests."""

from pathlib import Path

import pytest

from ..manager import AliasManager


aliases_data = {
    "eggs": Path("/home/monty/src/ham"),
    "ham": Path("/home/monty/src/ham"),
    "spam": Path("/home/monty/src/spam"),
}
aliases_toml = """\
["/home/monty/src/ham"]
aliases = ["eggs", "ham"]

["/home/monty/src/spam"]
aliases = ["spam"]
"""


@pytest.fixture
def aliases_path(tmp_path: Path) -> Path:
    """Return the path to a TOML file with alias definitions."""
    path = tmp_path / "aliases.toml"
    path.write_text(aliases_toml)
    return path


@pytest.fixture
def alias_manager(aliases_path: Path) -> AliasManager:
    """Return an :class:`AliasManager` instance with loaded aliases."""
    return AliasManager(aliases_path)
