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
Madam iso8601 module
"""
import re
from datetime import datetime, timedelta
from typing import Tuple, Union


def _get_isosplit(iso: str, split: str) -> Tuple[int, str]:
    """
    Return a tuple (n: int, iso: str) where n is the value split by split in iso

    :param iso: ISO 8601 string
    :param split: Split character
    :return:
    """
    if split in iso:
        value, _ = iso.split(split)
        n = int(value)
    else:
        n = 0
    return n, iso


def parse_isoduration(expression: str) -> timedelta:
    """
    Return a timeinterval instance from the ISO 8601 duration expression

    :param expression: ISO 8601 duration expression
    :return:
    """
    # Remove prefix
    expression = expression.split("P")[-1]

    # Step through letter dividers
    days, expression = _get_isosplit(expression, "D")
    _, expression = _get_isosplit(expression, "T")
    hours, expression = _get_isosplit(expression, "H")
    minutes, expression = _get_isosplit(expression, "M")
    seconds, expression = _get_isosplit(expression, "S")

    # Convert all to seconds
    return timedelta(
        days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds)
    )


def parse(expression: str) -> Union[datetime, Tuple[int, timedelta]]:
    """
    Return a tuple (with repeat count and timedelta interval)
    or a datetime after parsing the ISO 8601 expression

    :param expression:ISO 8601 expression
    :return:
    """
    if expression.startswith("R"):
        repeat_iso, duration_iso = expression.split("/")
        repeat_groups = re.compile("R(\\d?)").match(repeat_iso)
        if repeat_groups:
            repeat = int(repeat_groups.group(1))
        else:
            repeat = 0
        interval = parse_isoduration(duration_iso)
        return repeat, interval

    return datetime.fromisoformat(expression)


def iso_format_timedelta(value: timedelta) -> str:
    """
    Return iso8601 string notation of timedelta instance value

    :param value: Timedelta instance
    :return:
    """
    # split seconds to larger units
    seconds = value.total_seconds()
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    days, hours, minutes = map(int, (days, hours, minutes))
    seconds = round(seconds, 6)

    # build date
    date = ""
    if days:
        date = f"{days}D"

    # build time
    time = "T"
    # hours
    bigger_exists = date or hours
    if bigger_exists:
        time += f"{hours:02}H"
    # minutes
    bigger_exists = bigger_exists or minutes
    if bigger_exists:
        time += f"{minutes:02}M"
    # seconds
    if seconds.is_integer():
        seconds_str = f"{int(seconds):02}"
    else:
        # 9 chars long w/leading 0, 6 digits after decimal
        seconds_str = f"{seconds:09.6f}"
    # remove trailing zeros
    seconds_str = seconds_str.rstrip("0")
    time += f"{seconds_str}S"
    return f"P{date}{time}"
