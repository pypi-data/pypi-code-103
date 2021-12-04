# Copyright Louis Paternault 2015-2020
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Provide hook mechanism to builder"""

import contextlib
import functools


class Hook:
    """Hook executed at some named point during processing.

    Hooks instances of this class are never used.
    Hooks instances of subclasses are used.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, plugin):
        self.plugin = plugin
        self.shared = plugin.shared
        self.local = self.plugin.local


class ContextHook(Hook, contextlib.AbstractContextManager):
    """Hook executed before and after a context"""

    def __enter__(self, *args, **kwargs):
        # pylint: disable=useless-super-delegation
        return super().__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        # pylint: disable=useless-super-delegation
        return super().__exit__(*args, **kwargs)


class MethodHook(Hook):
    """Hook wrapping a method call."""

    # pylint: disable=too-few-public-methods

    def wrap(self, function):
        """Return a wrapped function."""
        # pylint: disable=no-self-use
        return function


def methodhook(*, getter=None):
    """Decorator to add hooks to a class method.

    :param function getter: Function that, given the instance object as argument,
        returns a :class:`plugins.PluginLoader` object. If ``None``, the default
        ``self.shared.builder.plugins`` is used (``self`` is supposed to have
        this attribute).
    """

    def decorator(function):
        """Actual decorator."""
        if function.__name__ == "__init__":
            hookname = function.__qualname__[: -len(function.__name__) - 1]
        else:
            hookname = function.__qualname__

        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            """Wrapped function."""
            self = args[0]
            if getter is None:
                plugins = self.shared.builder.plugins
            else:
                plugins = getter(*args, **kwargs)

            return plugins.apply_method_hook(hookname, function, *args, **kwargs)

        return wrapped

    return decorator
