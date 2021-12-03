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
This module provides mixins for model classes with certain properties.

They are designed to co-operate with other mixins and forwards unused
initialization arguments down to other mixins in the inheritance order.
"""
from abc import ABC
from typing import Set, Optional

from hifis_surveyval.models.mixins.uses_settings import UsesSettings
from hifis_surveyval.models.translated import Translated


class HasMandatory(ABC):
    """
    This mixin provides functionality for optional mandatory indicators.

    Model elements may require something to be present (e.g. an answer)
    directly or indirectly as a child of this object.
    """

    YAML_TOKEN = "mandatory"
    """The token used in metadata YAML files to indicate mandatory-ness."""

    def __init__(self, is_mandatory: bool, *args, **kwargs):
        """
        Initialize an object with mandatory-ness indicator.

        Args:
            is_mandatory:
                Whether this object has mandatory elements or not.
            *args:
                Will be forwarded to other mixins in the initialization order.
            **kwargs:
                Will be forwarded to other mixins in the initialization order.
        """
        super(HasMandatory, self).__init__(*args, **kwargs)
        self._is_mandatory = is_mandatory

    @property
    def is_mandatory(self) -> bool:
        """
        Check whether this question is marked as mandatory.

        Mandatory questions are expected to be answered by participants.

        Returns:
            True, if the question was marked as mandatory in the metadata,
            False otherwise
        """
        return self._is_mandatory


class HasLabel(ABC):
    """
    This mixin provides a label property.

    This is used as a shorthand for objects with more complex descriptions
    that do not fit nicely in some places (e.g. as labels for graph axis).
    """

    YAML_TOKEN = "label"
    """The token used in metadata YAML files to identify labels."""

    def __init__(self, label: str, *args, **kwargs):
        """
        Initialize a labelled object.

        Args:
            label:
                The label to be given to the object.
            *args:
                Will be forwarded to other mixins in the initialization order.
            **kwargs:
                Will be forwarded to other mixins in the initialization order.
        """
        super(HasLabel, self).__init__(*args, **kwargs)
        self._label = label

    @property
    def label(self) -> str:
        """
        Get the current label of the object.

        Returns:
            The current object label.
        """
        return self._label

    def relabel(self, new_label: str) -> None:
        """
        Set a new label for this object.

        If the new labels string representation is empty, nothing will be
        changed.

        Args:
            new_label:
                The new label to be used for the object. If required,
                the input will be cast to string before processing.
        """
        if not isinstance(new_label, str):
            new_label = str(new_label)
        if new_label:
            self._label = new_label


class HasText(ABC):
    """
    This mixin provides a text property.

    This is used as a more detailed description of the object, e.g. a
    verbatim question text. These texts may be translated, so when accessing
    them, providing a language is often required.
    """

    YAML_TOKEN = "text"
    """The token used in metadata YAML files to identify labels."""

    def __init__(self, translations: Translated, *args, **kwargs) -> None:
        """
        Initialize an object with a translatable description.

        Args:
            translations:
                The possible translations of the description.
            *args:
                Will be forwarded to other mixins in the initialization order.
            **kwargs:
                Will be forwarded to other mixins in the initialization order.
        """
        super(HasText, self).__init__(*args, **kwargs)
        self._text: Translated = translations

    def text(self, language_code: str) -> str:
        """
        Get the description text in a specific language.

        Args:
            language_code:
                The IETF code for the language.

        Returns:
            The translated description. if available.

        Raises:
            KeyError:
                If no translation for the requested language (with or
                without region code) can be found.
        """
        return self._text.get_translation(language_code=language_code)


class HasID(UsesSettings):
    """
    This is the abstract superclass for all objects that carry an ID.

    The ID is expected to be a string (or be convertible into such and to be
    unique among all identifiable objects.

    IDs are separated by a HIERARCHY_SEPARATOR and the part after the last
    separator forms the so-called "short ID".
    If no hierarchical parent_id is given, the short ID and the full ID are the
    same.
    """

    # TODO Move the repective YAML token in here

    known_ids: Set[str] = set()

    def __init__(
            self,
            object_id: str,
            parent_id: Optional[str] = None,
            *args,
            **kwargs,
    ) -> None:
        """
        Create a new identifiable object with a given ID.

        The class will track all known IDs to prevent duplicates.
        A full ID is formed by merging the parent's full ID (if it exists)
        and the object's ID.

        Args:
            object_id:
                A string serving as an ID to the object.
                It must be neither None nor empty.
            parent_id:
                (Optional, Default=None) The full ID of another identifiable
                object that forms the hierarchical parent of this one. Used
                to generate the full ID.
            *args:
                Will be forwarded to other mixins in the initialization order.
            **kwargs:
                Will be forwarded to other mixins in the initialization order.
        Raises:
            ValueError:
                Signals either a duplicate or invalid object_id
        """
        super(HasID, self).__init__(*args, **kwargs)

        if not object_id:
            raise ValueError(
                "ID of an identifiable object may neither be empty nor None"
            )

        if object_id in HasID.known_ids:
            raise ValueError(f"Attempted to assign duplicate ID {object_id}")

        self._full_id: str = (
            f"{parent_id}{self._settings.HIERARCHY_SEPARATOR}{object_id}"
            if parent_id
            else object_id
        )
        HasID.known_ids.add(self._full_id)

    def __del__(self) -> None:
        """
        Deconstruct an identifiable object.

        The used ID will be removed from the known IDs and can be re-used.
        """
        try:
            HasID.known_ids.remove(self._full_id)
            # FIXME For some reason removing the full ID from the list of
            #  known IDs fails due to them already being removed. But why?
            # This has been put into this little exception-catch box to not
            # spam the command line output, but I would prefer to understand
            # better what is going on here…
        except KeyError:
            pass

    @property
    def short_id(self) -> str:
        """
        Get the short ID of this object (without parent_id IDs).

        Returns:
            The string identifying this object with respect to its siblings
        """
        return self._full_id.split(self._settings.HIERARCHY_SEPARATOR)[-1]

    # TODO: Decide whether to cache the short id

    @property
    def full_id(self) -> str:
        """
        Get the full ID of the object (includes parent_id IDs).

        Returns:
            The string identifying the object with respect to any other
            HasID
        """
        return self._full_id

    def __str__(self) -> str:
        """Return the full ID as representation of this identifiable object."""
        return self.full_id
