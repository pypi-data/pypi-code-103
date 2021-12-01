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
from inspect import isclass

import click
from click.exceptions import UsageError
from lxml import etree

from .types import Bool


class Group(click.Group):
    """Group wrapper class that uses the custom decorators."""

    def __init__(self, *args, version, **kwargs):
        super().__init__(*args, **kwargs)

        # Backreference to a potential parent group.
        self.parent = None
        self.version = version

    def group(self, *args, **kwargs):
        """Shortcut decorator for subgroups."""
        from .decorators import group

        def decorator(func):
            cmd = group(*args, **kwargs)(func)
            self.add_command(cmd)
            return cmd

        return decorator

    def command(self, *args, **kwargs):
        """Shortcut decorator for commands."""
        from .decorators import command

        def decorator(func):
            cmd = command(*args, **kwargs)(func)
            self.add_command(cmd)
            return cmd

        return decorator

    def environment(self, *args, **kwargs):
        """Shortcut decorator for environments."""
        from .decorators import environment

        def decorator(func):
            env = environment(*args, **kwargs)(func)
            self.add_command(env)
            return env

        return decorator

    def add_command(self, cmd, name=None):
        cmd.parent = self

        # Inherit the group's version.
        if cmd.version is None:
            cmd.version = self.version

        super().add_command(cmd, name=name)


class Command(click.Command):
    """Command wrapper class with additional arguments."""

    tag = "program"

    def __init__(self, *args, description, example, version, **kwargs):
        super().__init__(*args, **kwargs)

        # Backreference to a potential parent group.
        self.parent = None
        self.description = description

        if self.description is None:
            self.description = self.help.split("\n")[0] if self.help else ""

        self.example = example
        self.version = version

        # Keep a map of options to easily retrieve them by their parameter name.
        self.option_map = {
            param.param_name: param
            for param in self.params
            if isinstance(param, Option)
        }

        # Perform some basic checks to ensure that relations are specified properly.
        for param_name, option in self.option_map.items():
            for attr in ["requires", "excludes"]:
                for relation in getattr(option, attr):
                    if param_name == relation:
                        raise ValueError(
                            f"Option '{param_name}' cannot require or exclude itself."
                        )

                    related_option = self.option_map.get(relation)

                    if related_option is None:
                        raise ValueError(
                            f"There is no option '{relation}' that option"
                            f" '{param_name}' can relate to."
                        )

                    if attr == "excludes" and (
                        option.default is not option.missing_value
                        or related_option.default is not related_option.missing_value
                    ):
                        raise ValueError(
                            f"Option '{param_name}' excludes option '{relation}', but"
                            " at least one of these options specifies a default value."
                        )

    def invoke(self, ctx):
        # Check the requirements and exclusions of all specified options.
        for param_name, option in self.option_map.items():
            if ctx.params[option.name] is option.missing_value:
                continue

            for requirement in option.requires:
                related_option = self.option_map[requirement]

                if ctx.params[related_option.name] is related_option.missing_value:
                    raise UsageError(
                        f"Option '{param_name}' requires option '{requirement}'."
                    )

            for exclusion in option.excludes:
                related_option = self.option_map[exclusion]

                if ctx.params[related_option.name] is not related_option.missing_value:
                    raise UsageError(
                        f"Option '{param_name}' excludes option '{exclusion}'."
                    )

        return super().invoke(ctx)

    def format_help(self, ctx, formatter):
        self.format_usage(ctx, formatter)

        if self.example:
            formatter.write_text(f"Example: {ctx.command_path} {self.example}")

        self.format_help_text(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

    def to_xml(self):
        """Convert the command to an XML tag."""
        program_elem = etree.Element(self.tag)

        name = self.name
        parent = self.parent

        while parent is not None:
            name = f"{parent.name} {name}"
            parent = parent.parent

        program_elem.set("name", name)

        if self.description:
            program_elem.set("description", self.description)

        if self.example:
            program_elem.set("example", f"{name} {self.example}")

        if self.version is not None:
            program_elem.set("version", self.version)

        return program_elem


class Environment(Command):
    """Command wrapper class for environments."""

    tag = "env"


class ParameterMixin:
    """Mixin that each parameter should inherit from."""

    def __init__(self, *args, description, param_type, exclude_from_xml, **kwargs):
        if isclass(param_type):
            param_type = param_type()

        super().__init__(*args, **kwargs, type=param_type)

        self.description = description
        self.param_type = param_type
        self.exclude_from_xml = exclude_from_xml

    def to_xml(self, index):
        """Convert the parameter to an empty XML tag."""
        param_elem = etree.Element("param")

        if self.description:
            param_elem.set("description", self.description)

        param_elem.attrib.update(self.param_type.xml_attrs)
        return param_elem


class Argument(ParameterMixin, click.Argument):
    """Argument wrapper class with additional arguments."""

    def to_xml(self, index):
        """Convert the argument to an XML tag.

        The tag will include the attributes corresponding to this argument.
        """
        param_elem = super().to_xml(index)

        param_elem.set("name", f"arg{index}")
        param_elem.set("positional", "true")

        if self.required:
            param_elem.set("required", "true")

        if self.default is not None:
            param_elem.set("default", self.param_type.to_string(self.default))

        if self.nargs != 1:
            param_elem.set("nargs", str(self.nargs))

        return param_elem


class Option(ParameterMixin, click.Option):
    """Option wrapper class with additional arguments."""

    def __init__(
        self,
        *args,
        name,
        description,
        param_type,
        default,
        char,
        is_flag,
        requires,
        excludes,
        exclude_from_xml,
        **kwargs,
    ):
        if is_flag:
            param_type = Bool
            default = False

        super().__init__(
            *args,
            **kwargs,
            description=description,
            param_type=param_type,
            default=default,
            is_flag=is_flag,
            help=description,
            exclude_from_xml=exclude_from_xml,
        )

        # Save the actual name of the option parameter separately, as the "name"
        # attribute is used by Click for the variable name.
        self.param_name = name
        self.char = char
        self.requires = requires if requires is not None else []
        self.excludes = excludes if excludes is not None else []

    @property
    def missing_value(self):
        """Get the value of this option if it would be missing.

        This value corresponds to ``False`` for flags and ``None`` otherwise.
        """
        return None if not self.is_flag else False

    def to_xml(self, index):
        """Convert the option to an XML tag.

        The tag will include the attributes corresponding to this option.
        """
        param_elem = super().to_xml(index)
        param_elem.set("name", self.param_name)

        if self.char is not None:
            param_elem.set("char", self.char)

        if self.is_flag:
            param_elem.set("type", "flag")

        if self.required:
            param_elem.set("required", "true")

        if self.default is not None:
            param_elem.set("default", self.param_type.to_string(self.default))

        if self.nargs != 1:
            param_elem.set("nargs", str(self.nargs))

        relations = list(self.requires) + [
            f"!{exclusion}" for exclusion in self.excludes
        ]

        if relations:
            relations = [relation.replace("|", "\\|") for relation in relations]
            param_elem.set("relations", "|".join(relations))

        return param_elem

    def get_default(self, ctx, call=True):
        """Get the default value of this option.

        If the parameter is a flag, i.e. ``is_flag`` is ``True``, then the default value
        for flags will be returned.
        """
        if self.is_flag:
            return self.default

        if click.__version__ >= "8.0":
            return super().get_default(ctx, call=call)

        return super().get_default(ctx)
