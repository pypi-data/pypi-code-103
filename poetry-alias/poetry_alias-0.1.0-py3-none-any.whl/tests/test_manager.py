"""Tests for the :mod:`poetry_alias.manager` module."""

from pathlib import Path
from typing import List

import pytest

from .conftest import aliases_data, aliases_toml
from ..exceptions import DuplicateAliasError, UnknownAliasError
from ..manager import AliasManager, AliasStore


class TestAliasManagerRepr:
    """Tests for :meth:`AliasManager.repr`."""

    def test_repr(self, aliases_path: Path) -> None:
        """Verify the representation for :class:`AliasManager` instances."""
        manager = AliasManager(aliases_path)
        assert repr(manager) == f"AliasManager(Path('{aliases_path}'))"


class TestAliasManagerAdd:
    """Tests for :meth:`AliasManager.add`."""

    def test_add_new_alias(self, alias_manager: AliasManager) -> None:
        """Test adding a new alias for a project."""
        alias = "fnord"
        path = Path("/tmp/src/fnord")
        alias_manager.add(alias, path)
        all_aliases = alias_manager.list()
        assert all_aliases[alias] == path

    def test_add_existing_alias_other_project(
        self, alias_manager: AliasManager
    ) -> None:
        """Test adding an existing alias for a different project."""
        with pytest.raises(DuplicateAliasError):
            alias_manager.add("ham", Path("/tmp/src/bogus/path"))

    def test_add_existing_alias_same_project(
        self, alias_manager: AliasManager
    ) -> None:
        """Test adding an existing alias for the same project."""
        existing_alias = "ham"
        project_path = aliases_data[existing_alias]
        try:
            alias_manager.add(existing_alias, project_path)
        except Exception as e:
            assert False, f"Exception raised: {e}"


class TestAliasManagerClean:
    """Tests for :meth:`AliasManager.clean`."""

    def test_return_removed_aliases(self, alias_manager: AliasManager) -> None:
        """Verify that the removed aliases are returned."""
        removed_aliases = alias_manager.clean()
        assert removed_aliases == aliases_data

    def test_clean_stores_empty_file(self, aliases_path: Path) -> None:
        """Check that the aliases file is empty after running ``clean()``."""
        manager = AliasManager(aliases_path)
        manager.clean()
        assert aliases_path.read_text() == ""


class TestAliasManagerGetAliases:
    """Tests for :meth:`AliasManager.get_aliases`."""

    @pytest.mark.parametrize(
        "project_path, aliases",
        [
            (Path("/home/monty/src/ham"), ["eggs", "ham"]),
            (Path("/home/monty/src/spam"), ["spam"]),
            (Path("/home/monty/src/foo"), []),
        ],
    )
    def test_return_value(
        self,
        alias_manager: AliasManager,
        project_path: Path,
        aliases: List[str],
    ) -> None:
        """Check the expected returned aliases for a project directory."""
        actual_aliases = alias_manager.get_aliases(project_path)
        assert actual_aliases == aliases


class TestAliasManagerGetProject:
    """Tests for :meth:`AliasManager.get_project`."""

    @pytest.mark.parametrize(
        "alias, expected_path",
        [
            ("eggs", Path("/home/monty/src/ham")),
            ("ham", Path("/home/monty/src/ham")),
            ("spam", Path("/home/monty/src/spam")),
        ],
    )
    def test_return_value(
        self, alias_manager: AliasManager, alias: str, expected_path: Path
    ) -> None:
        """Check the expected returned project path for an alias."""
        actual_path = alias_manager.get_project(alias)
        assert actual_path == expected_path

    def test_unknown_alias(self, alias_manager: AliasManager) -> None:
        """Test getting the project path for an unknown alias."""
        with pytest.raises(UnknownAliasError):
            alias_manager.get_project("fnord")


class TestAliasManagerList:
    """Tests for :meth:`AliasManager.list`."""

    def test_return_all_aliases(self, alias_manager: AliasManager) -> None:
        """Verify that all defined project aliases are returned."""
        all_aliases = alias_manager.list()
        assert all_aliases == aliases_data

    def test_does_not_return_internal_object(
        self, alias_manager: AliasManager
    ) -> None:
        """Ensure that a copy of the internal data is returned."""
        all_aliases = alias_manager.list()
        assert all_aliases is not alias_manager.aliases


class TestAliasManagerRemoveAlias:
    """Tests for :meth:`AliasManager.remove_alias`."""

    def test_remove_existing_alias(self, alias_manager: AliasManager) -> None:
        """Verify that removing an existing alias works."""
        alias_manager.remove_alias("ham")
        all_aliases = alias_manager.list()
        assert "ham" not in all_aliases

    def test_remove_non_existing_alias(
        self, alias_manager: AliasManager
    ) -> None:
        """Verify that removing a non-existing alias raises an exception."""
        with pytest.raises(UnknownAliasError):
            alias_manager.remove_alias("fnord")


class TestAliasManagerRemoveProject:
    """Tests for :meth:`AliasManager.remove_project`."""

    def test_remove_existing_project(
        self, alias_manager: AliasManager
    ) -> None:
        """Verify that removing an existing project works."""
        alias_manager.remove_project(Path("/home/monty/src/ham"))
        all_aliases = alias_manager.list()
        assert "ham" not in all_aliases
        assert "eggs" not in all_aliases

    def test_remove_non_existing_project(
        self, alias_manager: AliasManager
    ) -> None:
        """Verify that removing a non-existing project is a no-op."""
        try:
            alias_manager.remove_project(Path("/tmp/foo"))
        except Exception as e:
            assert False, f"Exception raised: {e}"


class TestAliasStore:
    """Tests for the :class:`AliasStore` class."""

    def test_repr(self, aliases_path: Path) -> None:
        """Verify the representation for :class:`AliasStore` instances."""
        store = AliasStore(aliases_path)
        assert repr(store) == f"AliasStore(Path('{aliases_path}'))"

    def test_load(self, aliases_path: Path) -> None:
        """Check that ``load()`` returns the expected data structure."""
        store = AliasStore(aliases_path)
        aliases = store.load()
        assert aliases == aliases_data

    def test_save(self, aliases_path: Path) -> None:
        """Check that ``save()`` correctly stores aliases as TOML."""
        store = AliasStore(aliases_path)
        store.save(aliases_data)
        actual = aliases_path.read_text()
        assert actual == aliases_toml
