#!/usr/bin/env python3

# Cagou: desktop/mobile frontend for Salut à Toi XMPP client
# Copyright (C) 2016-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from kivy import utils as kivy_utils


def create():
    """Factory method to create the platform instance adapted to running one"""
    if kivy_utils.platform == "android":
        from .android import Platform
        return Platform()
    else:
        from .base import Platform
        return Platform()
