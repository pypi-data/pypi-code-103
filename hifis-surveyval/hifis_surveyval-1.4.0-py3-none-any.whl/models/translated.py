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

"""Models survey elements that can be represented in multiple languages."""

from typing import Dict, List

from schema import And, Regex, Schema

from hifis_surveyval.models.mixins.yaml_constructable import (
    YamlConstructable,
    YamlDict,
)


class Translated(YamlConstructable):
    """
    A wrapper around text instances with multiple translations.

    Languages are identified by their ISO 693-1 two-letter codes.
    Optionally an uppercase region identifier may be appended as well. Region
    identifiers consist of a two or three letter code and must be separated by
    a dash from the language identifier.

    Examples for valid identifiers are `de`, `en-US` but not `frFR`.
    """

    schema = Schema(
        {
            And(str, Regex("^[a-z]{2}(-[A-Z]{2,3})?$")): And(
                str,
                lambda s: s,
                error="Translation must neither be empty nor None",
            )
        }
    )
    """
    The validation schema used for translation dictionaries.
    * The dictionary may not be empty
    * The key must exist, be a string and consist of two lower-case letters
    * The value must be a string and must not be empty
    """
    # TODO: Properly format this docstring

    def __init__(self, translations: Dict[str, str]):
        """
        Create a new instance of translated text.

        Args:
            translations:
                A mapping from the language code to the translation in the
                respective language. The dictionary must not be empty.
                Keys are expected to be two-letter codes with an optional
                region code, and values must neither be None nor be empty.
        """
        self._translations = Translated.schema.validate(translations)

    def available_languages(self) -> List[str]:
        """
        Get all languages for which translations exist.

        Returns:
            A list of language codes
        """
        return list(self._translations.keys())

    def get_translation(self, language_code: str) -> str:
        """
        Get the translation for a specific language.

        If the passed in language code has a region specifier, and no
        translation for this region is given, a translation with only the
        language code will be looked up as a fallback.

        Args:
            language_code:
                The ISO 693-1 two letter code for the language the text is
                requested for. Optionally a dash followed by an uppercase
                two or three letter region code may be appended as well.
        Returns:
            The text in the requested language or None if no translation for
            this language exists.
        Raises:
            KeyError:
                If no translation for the requested language (with or
                without region code) can be found.
        """
        try:
            return self._translations[language_code]
        except KeyError:
            pass
        try:
            return self._translations[language_code[0:1]]
        except KeyError:
            raise KeyError(
                f"No translation for {language_code} in {self._translations}"
            )

    @staticmethod
    def _from_yaml_dictionary(yaml: YamlDict, **kwargs) -> "Translated":
        """
        Construct a new Translated instance from the given data.

        The validation of the dictionaries keys and values are done by the
        Translated-constructor.

        Args:
            yaml:
                The YamlDict representing the translations.
                Keys are expected to be language and optional region codes and
                values are supposed to be the appropriate translations.

        Returns:
            A new Translated-instance as given in the YAML data.
        """
        return Translated(yaml)
