#!/usr/bin/env python3
#
# Series of Wokkel patches used by SàT
# Copyright (C) 2015-2019 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2015 Adien Cossa (souliane@mailoo.org)

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

installed = False

def install():
    """Monkey patch Wokkel to have improvments implemented here"""
    global installed
    if not installed:
        from twisted.python import compat
        compat._PY3 = True
        import wokkel
        from . import pubsub, rsm, mam, data_form
        wokkel.pubsub = pubsub
        wokkel.rsm = rsm
        wokkel.mam = mam
        data_form.install()
        installed = True
