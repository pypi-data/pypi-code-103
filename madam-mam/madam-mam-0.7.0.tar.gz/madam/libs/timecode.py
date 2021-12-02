# Copyright 2021 Vincent Texier
#
# This file is part of MADAM.
#
# MADAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MADAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MADAM.  If not, see <https://www.gnu.org/licenses/>.

"""
Madam timecode module
"""


class TimecodeSeconds:
    """
    Madam TimecodeSeconds class
    """

    def __init__(self, seconds: float):
        """
        Create TimecodeSeconds instance from seconds

        :param seconds: Seconds to convert
        """
        self.seconds = seconds

    def __repr__(self) -> str:
        """
        Return a string representation of Timecode in seconds (HH:MM:SS.mmm)

        ex: 00:01:02.123

        :return:
        """
        hours = int(self.seconds // 3600)
        minutes = int((self.seconds - (hours * 3600)) // 60)
        seconds = float(self.seconds - (hours * 3600) - (minutes * 60))

        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
