"""Tests for the :mod:`poetry_alias.plugin` module."""

from poetry.plugins.application_plugin import ApplicationPlugin

from ..commands import AliasCommand
from ..plugin import AliasPlugin, is_alias_command_class


def test_alias_plugin_is_poetry_application_plugin() -> None:
    """Verify that :class:`AliasPlugin` is a Poetry application plugin."""
    assert issubclass(AliasPlugin, ApplicationPlugin)


class TestIsAliasCommandClass:
    """Tests for :func:`is_alias_command_class`."""

    def test_arbitrary_object(self) -> None:
        """Verify that an arbitrary object is not an alias command."""
        assert is_alias_command_class(4711) is False

    def test_arbitrary_class(self) -> None:
        """Verify that an arbitrary class is not an alias command."""
        assert is_alias_command_class(str) is False

    def test_alias_command_base_class(self) -> None:
        """Verify that the alias command base class itself is not a command."""
        assert is_alias_command_class(AliasCommand) is False

    def test_alias_command_subclass(self) -> None:
        """Verify that an :class:`AliasCommand` subclass is a valid command."""
        # noinspection PyPep8Naming
        MyCommand = type("MyCommand", (AliasCommand,), {})
        assert is_alias_command_class(MyCommand) is True
