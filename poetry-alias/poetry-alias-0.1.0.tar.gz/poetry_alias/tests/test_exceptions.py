"""Tests for the :mod:`poetry_alias.exceptions` module."""

from pathlib import Path

import pytest

from ..exceptions import (
    DuplicateAliasError,
    PoetryAliasError,
    UnknownAliasError,
)


@pytest.mark.parametrize("cls", [DuplicateAliasError])
def test_is_poetry_alias_error_subclass(cls: type) -> None:
    """Check that an exception is a subclass of :class:`PoetryAliasError`."""
    assert issubclass(cls, PoetryAliasError)


class TestDuplicateAliasError:
    """Tests for :class:`DuplicateAliasError`."""

    def test_repr(self) -> None:
        """Test the representation string."""
        exc = DuplicateAliasError("foo", Path("/tmp/foo"))
        assert repr(exc) == "DuplicateAliasError('foo', Path('/tmp/foo'))"

    def test_str(self) -> None:
        """Test the string representation."""
        exc = DuplicateAliasError("foo", Path("/tmp/foo"))
        assert str(exc) == "Alias `foo` already exists for project /tmp/foo"


class TestUnknownAliasError:
    """Tests for :class:`UnknownAliasError`."""

    def test_repr(self) -> None:
        """Test the representation string."""
        exc = UnknownAliasError("foo")
        assert repr(exc) == "UnknownAliasError('foo')"

    def test_str(self) -> None:
        """Test the string representation."""
        exc = UnknownAliasError("foo")
        assert str(exc) == "Alias `foo` does not exist"
