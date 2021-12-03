# hifis-surveyval
# Framework to help developing analysis scripts for the HIFIS Software survey.
#
# SPDX-FileCopyrightText: 2021 HIFIS Software <support@hifis.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Provides an abstract class for classes constructed from YAML-Dictionaries.

All of these inheriting classes should define a Schema to dictate the required
structure of the YAML to be parsed.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union

from schema import Or, Schema, SchemaError

# A shorthand type for the kind of lists and dictionaries that can be
# encountered when parsing YAML data
YamlList = List[Union[str, "YamlDict"]]
YamlDict = Dict[str, Union[str, "YamlList", "YamlDict"]]


class YamlConstructable(ABC):
    """
    An abstract class for classes that can be instantiated from a YamlDict.

    It defines a catchall schema that accepts everything that looks like a
    valid YAML mapping.
    """

    schema: Schema = Schema({str: Or(str, list, dict)})
    """ The default schema of a YamlConstructable validates everything which
    is formatted like a YamlDictionary"""

    @staticmethod
    @abstractmethod
    def _from_yaml_dictionary(yaml: YamlDict, **kwargs) -> "YamlConstructable":
        """
        Instantiate an object of this class from a given YamlDict.

        This must be overridden by inheriting classes.

        Args:
            yaml:
                A dictionary containing the data required to create a new
                instance of the inheriting class. The dictionary has been
                validated against the schema provided by the inheriting class.
        Returns:
            A new instance of the overriding subclass
        """
        pass

    @classmethod
    def from_yaml_dictionary(
        cls, yaml: YamlDict, **kwargs
    ) -> "YamlConstructable":
        """
        Instantiate an object of this class from a given YamlDict.

        The given YAML will be validated against the schema defined for the
        class. If the class did not define a schema  on its own (although it
        should) a catchall schema is provided.

        Args:
            yaml:
                A dictionary as received from the YAML parser containing the
                data required to create a new instance of the inheriting class
        Returns:
            A new instance of the overriding subclass
        """
        schema: Schema = cls.schema
        try:
            validated_yaml = schema.validate(yaml)
            return cls._from_yaml_dictionary(yaml=validated_yaml, **kwargs)
        except SchemaError as validation_error:
            # Construct a reduces YAML representation to limit the output in
            # the error message to the essentials.
            # This generator expression basically constructs a copy of the
            # top YAML object, but all values that are either lists or
            # dictionaries themselves will be replaced by the text "…"
            reduced_yaml = {
                key: (
                    "…" if isinstance(value, dict) or isinstance(value, list)
                    else value
                )
                for (key, value) in yaml.items()
            }
            raise ValueError(f"{validation_error} when parsing {reduced_yaml}")
