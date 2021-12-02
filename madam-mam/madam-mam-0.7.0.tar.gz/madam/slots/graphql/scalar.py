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

from datetime import datetime, timedelta

from ariadne import ScalarType

from madam.libs.iso8601 import iso_format_timedelta

datetime_scalar = ScalarType("Datetime")
timedelta_scalar = ScalarType("Timedelta")


@datetime_scalar.serializer
def serialize_datetime(value: datetime) -> str:
    """
    Serialize timedelta value to iso8601 string notation

    :param value: Timedelta value
    :return:
    """
    return value.isoformat()


@timedelta_scalar.serializer
def serialize_timedelta(value: timedelta) -> str:
    """
    Serialize timedelta value to iso8601 string notation

    :param value: Timedelta value
    :return:
    """
    return iso_format_timedelta(value)
