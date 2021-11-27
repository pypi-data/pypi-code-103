# -----------------------------------------------------------------------------
# Copyright (c) 2020 J. Matt Roberts
# Copyright (c) 2015-2019 Silicondust, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.
# -----------------------------------------------------------------------------

class NoCompatibleDevicesException(Exception):
    pass


class NoTunersException(Exception):
    pass


class NoDeviceAuthException(Exception):
    pass


class EmptyLineupException(Exception):
    pass


class NoGuideDataException(Exception):
    pass


class RuleModException(Exception):
    pass


class RuleDelException(Exception):
    pass


class SeriesHideException(Exception):
    pass


class RecordingDelException(Exception):
    pass
