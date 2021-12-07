# Copyright 2019, 2020 Dominik George <dominik.george@teckids.org>
# Copyright 2020 Jonathan Weth <wethjo@katharineum.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import locale
from typing import Optional, Sequence, Tuple, Union

from .util import normalise_locale


@dataclass
class CalendarWeek:
    """ A calendar week defined by year and ISO week number. """

    year: Optional[int] = None
    week: Optional[int] = None

    @classmethod
    def day_names(cls, loc: Optional[str] = None) -> Tuple[str]:
        """ Return a tuple of day names for the selected locale. """

        with calendar.different_locale(normalise_locale(loc)):
            return tuple(calendar.day_name)

    @classmethod
    def day_abbrs(cls, loc: Optional[str] = None) -> Tuple[str]:
        """ Return a tuple of day name abbreviations for the selected locale. """

        with calendar.different_locale(normalise_locale(loc)):
            return tuple(calendar.day_abbr)

    @classmethod
    def month_names(cls, loc: Optional[str] = None) -> Tuple[str]:
        """ Return a tuple of month names for the selected locale. """

        with calendar.different_locale(normalise_locale(loc)):
            return tuple(calendar.month_name[1:])

    @classmethod
    def month_abbrs(cls, loc: Optional[str] = None) -> Tuple[str]:
        """ Return a tuple of month name abbreviations for the selected locale. """

        with calendar.different_locale(normalise_locale(loc)):
            return tuple(calendar.month_abbr[1:])

    @classmethod
    def from_date(cls, when: date):
        """ Get the calendar week by a date object (the week this date is in). """

        week = int(when.strftime("%V"))
        year = when.year

        if when.month == 12 and week == 1:
            year += 1
        elif when.month == 1 and (week == 52 or week == 53):
            year -= 1

        return cls(year=year, week=week)

    @classmethod
    def current_week(cls) -> int:
        """ Get the current week number. """

        return cls().week

    @classmethod
    def weeks_within(cls, start: date, end: date) -> Sequence[CalendarWeek]:
        """ Get all calendar weeks within a date range. """

        if start > end:
            raise ValueError("End date must be after start date.")

        current = start
        weeks = []
        while current < end:
            weeks.append(cls.from_date(current))
            current += timedelta(days=7)

        return weeks

    @classmethod
    def get_last_week_of_year(cls, year: int) -> CalendarWeek:
        """Get the last week of a year."""

        last_week = date(year, 12, 28).isocalendar()[1]
        return cls(week=last_week, year=year)

    def __post_init__(self) -> None:
        today = date.today()

        if not self.year:
            self.year = today.year
        if not self.week:
            self.week = int(today.strftime("%V"))

    def __str__(self) -> str:
        return "Week %d (%s to %s)" % (self.week, self[0], self[-1],)

    def __len__(self) -> int:
        return 7

    def __getitem__(self, n: int) -> date:
        if n < -7 or n > 6:
            raise IndexError("Week day %d is out of range." % n)

        if n < 0:
            n += 7

        return datetime.strptime("%d-%d-%d" % (self.year, self.week, n + 1), "%G-%V-%u").date()

    def __contains__(self, day: date) -> bool:
        return self.__class__.form_date(day) == self

    def __eq__(self, other: CalendarWeek) -> bool:
        return self.year == other.year and self.week == other.week

    def __lt__(self, other: CalendarWeek) -> bool:
        return self[0] < other[0]

    def __gt__(self, other: CalendarWeek) -> bool:
        return self[0] > other[0]

    def __le__(self, other: CalendarWeek) -> bool:
        return self[0] <= other[0]

    def __gr__(self, other: CalendarWeek) -> bool:
        return self[0] >= other[0]

    def __add__(self, weeks: int) -> CalendarWeek:
        return self.__class__.from_date(self[0] + timedelta(days=weeks * 7))

    def __sub__(self, weeks: int) -> CalendarWeek:
        return self.__class__.from_date(self[0] - timedelta(days=weeks * 7))
