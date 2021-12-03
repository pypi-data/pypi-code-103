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
This module contains the base class for all objects that carry a unique ID.

IDs are composed of multiple parts interjected by a hierarchy separator.
"""
from abc import ABC

from hifis_surveyval.core.settings import Settings


class UsesSettings(ABC):
    """
    This is a mixin for objects that need access to the settings to function.

    It caches a reference to the settings instance.
    """

    def __init__(self, settings: Settings, *args, **kwargs):
        """
        Initialize an object that uses the application settings.

        Args:
            settings:
                The applications settings object.
            *args:
                Will be forwarded to other mixins in the initialization order.
            **kwargs:
                Will be forwarded to other mixins in the initialization order.
        """
        super(UsesSettings, self).__init__(*args, **kwargs)

        if not settings:
            raise ValueError(
                "This object requires access to the application settings"
            )

        self._settings: Settings = settings
