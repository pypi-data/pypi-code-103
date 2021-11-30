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
import click


class ParamTypeMixin:
    """Mixin that each parameter type should inherit from.

    Each parameter should at the very least have a ``name`` attribute.
    """

    name = "param"

    @property
    def xml_attrs(self):
        """Get the XML attributes of this parameter type.

        For use in the xmlhelp of the arguments and options.

        :return: A dictionary representing the XML attributes.
        """
        return {
            "type": self.name,
        }

    @classmethod
    def to_string(cls, value):
        """Convert one or multiple values of this parameter type to a string.

        By default, values are simply converted to their standard string representation.
        Multiple values, which are represented as tuples, are combined with spaces
        inbetween. Spaces being part of the resulting string values will be escaped with
        a backslash.

        :param value: The value to convert.
        :return: The converted string value.
        """
        if isinstance(value, tuple):
            return " ".join([str(val).replace(" ", "\\ ") for val in value])

        return str(value).replace(" ", "\\ ")


class String(ParamTypeMixin, click.types.StringParamType):
    """String parameter type."""

    name = "string"

    def convert(self, value, param, ctx):
        # Ensure that default parameter values always get converted to a string as well.
        return str(super().convert(value, param, ctx))


class TokenList(String):
    """Token list parameter type.

    Similar to regular strings, but uses a specified separator value to split the given
    string value into a list of strings.

    :param separator: (optional) The separator to use for splitting the values.
    """

    name = "tokenlist"

    def __init__(self, separator=","):
        self.separator = separator

    @property
    def xml_attrs(self):
        """See :meth:`ParamTypeMixin.xml_attrs`.

        Additionally includes the separator used for splitting values.
        """
        return {
            **super().xml_attrs,
            "separator": self.separator,
        }

    def convert(self, value, param, ctx):
        if isinstance(value, list):
            return value

        value = super().convert(value, param, ctx)
        return value.split(self.separator)


class Bool(ParamTypeMixin, click.types.BoolParamType):
    """Boolean parameter type."""

    name = "bool"

    @staticmethod
    def _bool_to_string(value):
        if value is True:
            return "true"

        return "false"

    @classmethod
    def to_string(cls, value):
        """See :meth:`ParamTypeMixin.to_string`.

        ``True`` will be converted to ``'true'``, ``False`` to ``'false'``.
        """
        if isinstance(value, tuple):
            return " ".join([cls._bool_to_string(val) for val in value])

        return cls._bool_to_string(value)


class Integer(ParamTypeMixin, click.types.IntParamType):
    """Integer parameter type."""

    # name = 'int'
    name = "long"  # Compatibility with the current xmlhelp interface.


class IntRange(ParamTypeMixin, click.types.IntRange):
    """Integer range parameter type.

    :param min: (optional) The minimum allowed integer value.
    :param max: (optional) The maximum allowed integer value.
    """

    # name = "int_range"
    name = "long_range"  # Compatibility with the current xmlhelp interface.

    def __init__(self, min=None, max=None):
        min = int(min) if min is not None else min
        max = int(max) if max is not None else max
        super().__init__(min=min, max=max)

    @property
    def xml_attrs(self):
        """See :meth:`ParamTypeMixin.xml_attrs`.

        Additionally includes the minimum and maximum allowed integer values, if
        present.
        """
        attrs = {
            **super().xml_attrs,
        }

        if self.min is not None:
            attrs["min"] = str(self.min)

        if self.max is not None:
            attrs["max"] = str(self.max)

        return attrs


class Float(ParamTypeMixin, click.types.FloatParamType):
    """Float parameter type."""

    # name = 'float'
    name = "real"  # Compatibility with the current xmlhelp interface.


class FloatRange(ParamTypeMixin, click.types.FloatRange):
    """Float range parameter type.

    :param min: (optional) The minimum allowed float value.
    :param max: (optional) The maximum allowed float value.
    """

    # name = "float_range"
    name = "real_range"  # Compatibility with the current xmlhelp interface.

    def __init__(self, min=None, max=None):
        min = float(min) if min is not None else min
        max = float(max) if max is not None else max
        super().__init__(min=min, max=max)

    @property
    def xml_attrs(self):
        """See :meth:`ParamTypeMixin.xml_attrs`.

        Additionally icludes the minimum and maximum allowed float values, if present.
        """
        attrs = {
            **super().xml_attrs,
        }

        if self.min is not None:
            attrs["min"] = str(self.min)

        if self.max is not None:
            attrs["max"] = str(self.max)

        return attrs


class Choice(ParamTypeMixin, click.types.Choice):
    """Choice parameter type.

    :param choices: A list or tuple of valid strings to choose from.
    :param case_sensitive: (optional) Whether the choices are case sensitive.
    """

    name = "choice"

    def __init__(self, choices, case_sensitive=False):
        choices = [str(choice) for choice in choices]
        super().__init__(choices, case_sensitive=case_sensitive)

    @property
    def xml_attrs(self):
        r"""See :meth:`ParamTypeMixin.xml_attrs`.

        Additionally includes all possible choices, separated by a single vertical bar,
        and whether the choices are case sensitive. Bars being part of a choice will be
        escaped with a backslash.
        """
        choices = [choice.replace("|", "\\|") for choice in self.choices]

        attrs = {
            **super().xml_attrs,
            "choices": "|".join(choices),
            "case_sensitive": Bool.to_string(self.case_sensitive),
        }

        return attrs


class Path(ParamTypeMixin, click.types.Path):
    """Path parameter type.

    :param path_type: (optional) The type of path to accept, one of ``'directory'`` or
        ``'file'``. Will be used in the path check if ``exists`` is ``True``.
        Additionally, the name of this parameter to be used in the xmlhelp will be
        changed from ``path`` to ``'directory'`` or ``'file'``
    :param exists: (optional) Flag indicating whether to check if the path exists.
    """

    name = "path"

    def __init__(self, path_type=None, exists=False):
        file_okay = dir_okay = True

        if path_type == "directory":
            self.name = path_type
            file_okay = False

        if path_type == "file":
            self.name = path_type
            dir_okay = False

        super().__init__(exists=exists, file_okay=file_okay, dir_okay=dir_okay)

    @property
    def xml_attrs(self):
        """See :meth:`ParamTypeMixin.xml_attrs`.

        Additionally includes the ``exists`` flag.
        """
        attrs = {
            **super().xml_attrs,
            "exists": Bool.to_string(self.exists),
        }

        return attrs
