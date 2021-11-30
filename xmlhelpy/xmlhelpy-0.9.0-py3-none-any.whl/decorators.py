# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import keyword
import string

import click

from .core import Argument
from .core import Command
from .core import Environment
from .core import Group
from .core import Option
from .formatting import print_commands
from .formatting import print_version
from .formatting import print_xmlhelp
from .types import String


def _duplicate_param(func, msg):
    function_name = (
        f"{func.__module__}.{func.__name__}"
        if func.__module__ is not None
        else func.__name__
    )
    raise ValueError(f"{function_name}: {msg}")


def _check_name(func, name):
    if not hasattr(func, "_param_names"):
        func._param_names = set()

    if name in func._param_names:
        _duplicate_param(func, f"Name '{name}' specified twice.")

    func._param_names.add(name)


def _check_char(func, name, char):
    if char is not None:
        if not hasattr(func, "_param_chars"):
            func._param_chars = set()

        if char in func._param_chars:
            _duplicate_param(func, f"Char '{char}' specified twice.")

        func._param_chars.add(char)


def group(name=None, version=None, cls=Group):
    """Decorator to register a new command group.

    Group names will be listed before the actual command name in the generated xmlhelp.

    :param name: (optional) The name of the group. Defaults to the name of the decorated
        function with underscores replaced by dashes.
    :param version: (optional) The version of the group as string. This version will be
        inherited by all commands and subgroups of this group that do not explicitely
        specify their own version.
    :param cls: (optional) The class to use for the command group.
    """

    def decorator(func):
        _check_name(func, "commands")

        click.option(
            "--commands",
            help="Print a list of all commands this group contains and exit.",
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=print_commands,
        )(func)

        _check_name(func, "version")

        click.option(
            "--version",
            help="Print the version of this group and exit.",
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=print_version,
        )(func)

        return click.group(cls=cls, name=name, version=version)(func)

    return decorator


def command(name=None, description=None, example=None, version=None, cls=Command):
    """Decorator to register a new command or underlying tool.

    :param name: (optional) The name of the command. Defaults to the name of the
        decorated function with underscores replaced by dashes.
    :param description: (optional) The description of the command to be shown in the
        xmlhelp. Defaults to the first line of the docstring of the decorated function.
    :param example: (optional) An example parametrization of using the command.
    :param version: (optional) The version of the command as string.
    :param cls: (optional) The class to use for the command.
    """

    def decorator(func):
        _check_name(func, "xmlhelp")

        click.option(
            "--xmlhelp",
            help="Print the xmlhelp of this command and exit.",
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=print_xmlhelp,
        )(func)

        _check_name(func, "version")

        click.option(
            "--version",
            help="Print the version of this command and exit.",
            is_flag=True,
            is_eager=True,
            expose_value=False,
            callback=print_version,
        )(func)

        # Clear the saved name and char information, so each command is checked
        # separately.
        if hasattr(func, "_param_names"):
            del func._param_names
        if hasattr(func, "_param_chars"):
            del func._param_chars

        cmd = click.command(
            cls=cls,
            name=name,
            version=version,
            example=example,
            description=description,
        )(func)

        return cmd

    return decorator


def environment(
    name=None, description=None, example=None, version=None, cls=Environment
):
    """Decorator to register a new environment.

    Environments are almost identical to regular commands. They automatically include
    the ``--env-exec`` option and use the ``env`` tag for the root element in the
    xmlhelp.

    :param name: (optional) The name of the environment. Defaults to the name of the
        decorated function with underscores replaced by dashes.
    :param description: (optional) The description of the environment to be shown in the
        xmlhelp. Defaults to the first line of the docstring of the decorated function.
    :param example: (optional) An example parametrization of using the environment.
    :param version: (optional) The version of the environment as string.
    :param cls: (optional) The class to use for the environment.
    """

    def decorator(func):
        _check_name(func, "env-exec")

        click.option(
            "--env-exec",
            help="Command string to be executed inside the environment.",
            multiple=True,
            required=True,
        )(func)

        env = command(
            cls=cls,
            name=name,
            version=version,
            example=example,
            description=description,
        )(func)

        return env

    return decorator


def argument(
    name,
    description="",
    nargs=1,
    param_type=String,
    required=True,
    default=None,
    exclude_from_xml=False,
):
    """Decorator to add an argument parameter to a command.

    Arguments are positional parameters with less possibilities than options that are
    also required by default.

    :param name: The name of the argument. Will also be used for the variable name, with
        dashes replaced by underscores.
    :param description: (optional) The description of the argument.
    :param nargs: (optional) The number of values (separated by spaces) to expect.
        ``-1`` can be specified for a single argument to allow for an unlimited number
        of values.
    :param param_type: (optional) The type of the argument parameter, either as class or
        instance. See :mod:`xmlhelpy.types` for the possible parameter types.
    :param required: (optional) Flag indicating whether the argument is required or not.
    :param default: (optional) The default value to take if the argument is not given.
    :param exclude_from_xml: (optional) Flag indicating whether the argument should be
        excluded from the xmlhelp output.
    """

    def decorator(func):
        _check_name(func, name)

        click.argument(
            name,
            cls=Argument,
            description=description,
            nargs=nargs,
            param_type=param_type,
            required=required,
            default=default,
            exclude_from_xml=exclude_from_xml,
        )(func)

        return func

    return decorator


def option(
    name,
    description="",
    nargs=1,
    param_type=String,
    required=False,
    default=None,
    exclude_from_xml=False,
    char=None,
    var_name=None,
    is_flag=False,
    requires=None,
    excludes=None,
):
    """Decorator to add an option parameter to a command.

    Options are non-positional parameters or flags.

    :param name: The full name of the option, which has to be given as
        ``--<name> <value>`` when invoking the command. Will also be used for the
        variable name, with dashes replaced by underscores.
    :param description: (optional) The description of the option.
    :param nargs: (optional) The number of values (separated by spaces) to expect.
    :param param_type: (optional) The type of the option parameter, either as class or
        instance. See :mod:`xmlhelpy.types` for the possible parameter types.
    :param required: (optional) Flag indicating whether the option is required or not.
    :param default: (optional) The default value to take if the option is not given.
    :param exclude_from_xml: (optional) Flag indicating whether the option should be
        excluded from the xmlhelp output.
    :param char: (optional) A shorthand for an option consisting of a single ASCII
        letter, which has to be given as ``-<char> <value>`` when invoking the command.
    :param var_name: (optional) A custom variable name to use instead of the parameter
        name.
    :param is_flag: (optional) Flag indicating whether the option is a flag. Flags are
        special options that do not require a value. They always use :class:`.Bool` as
        type and ``False`` as default value. Additionally, their type is specified as
        ``flag`` in the xmlhelp.
    :param requires: (optional) A list of option names which should be required when
        using this option. The requirements are set up in both directions automatically.
    :param excludes: (optional) A list of option names which should be excluded when
        using this option. The exclusions are set up in both directions automatically.
    """

    def decorator(func):
        # It is best to deal with the parameter names here already before passing them
        # to the original option decorator.
        if "/" in name:
            raise click.BadOptionUsage(name, "Names cannot contain slashes.")

        if char is not None and char not in string.ascii_letters:
            raise click.BadOptionUsage(name, "Chars cannot contain special characters.")

        if var_name is not None and (
            keyword.iskeyword(var_name) or not var_name.isidentifier()
        ):
            raise click.BadOptionUsage(
                name, "Variable names cannot be reserved keywords or identifiers."
            )

        _check_name(func, name)
        _check_char(func, name, char)

        param_decls = ["--" + name]

        if char is not None:
            param_decls.append("-" + char)

        if var_name is not None:
            param_decls.append(var_name)

        click.option(
            *param_decls,
            cls=Option,
            name=name,
            description=description,
            nargs=nargs,
            param_type=param_type,
            required=required,
            default=default,
            exclude_from_xml=exclude_from_xml,
            char=char,
            is_flag=is_flag,
            requires=requires,
            excludes=excludes,
            show_default=True,
        )(func)

        return func

    return decorator
