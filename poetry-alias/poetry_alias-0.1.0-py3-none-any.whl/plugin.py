"""The ``poetry-alias`` application plugin for Poetry."""

import inspect
from typing import Any

from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin

from . import commands
from .commands import AliasCommand


class AliasPlugin(ApplicationPlugin):
    """A Poetry plugin which adds an ``alias`` CLI command suite."""

    def activate(self, application: Application) -> None:
        """Activate the plugin.

        This registers all :class:`AliasCommand` subclasses contained in
        the :module:`command` module as new Poetry commands.
        """
        command_classes = [
            item[1]
            for item in inspect.getmembers(commands, is_alias_command_class)
        ]
        for cls in command_classes:
            application.command_loader.register_factory(
                cls.name, lambda c=cls: c()
            )


def is_alias_command_class(obj: Any) -> bool:
    """Check whether a given object is a subclass of :class:`AliasCommand`.

    :param obj: the object to check.
    :return: ``true`` if the provided object is a subclass of
             :class:`AliasCommand`, and ``false`` otherwise.
    """
    # noinspection PyTypeChecker
    return (
        inspect.isclass(obj)
        and issubclass(obj, AliasCommand)
        and obj is not AliasCommand
    )
