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

import json
import locale
from typing import Any, List, Optional, Tuple

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.encoding import DEFAULT_LOCALE_ENCODING
from django.utils.functional import lazy
from django.utils.translation import get_language, to_locale

from .calendarweek import CalendarWeek


def i18n_day_names(loc: Optional[str] = None) -> Tuple[str]:
    """ Return a tuple of day names for the current locale. """

    if loc is None:
        loc = to_locale(get_language() or settings.LANGUAGE_CODE)

    try:
        return CalendarWeek.day_names(loc)
    except locale.Error:
        return CalendarWeek.day_names()


def i18n_day_abbrs(loc: Optional[str] = None) -> Tuple[str]:
    """ Return a tuple of day name abbreviations for the current locale. """

    if loc is None:
        loc = to_locale(get_language() or settings.LANGUAGE_CODE)

    try:
        return CalendarWeek.day_abbrs(loc)
    except locale.Error:
        return CalendarWeek.day_abbrs()


def i18n_month_names(loc: Optional[str] = None) -> Tuple[str]:
    """ Return a tuple of month names for the current locale. """

    if loc is None:
        loc = to_locale(get_language() or settings.LANGUAGE_CODE)

    try:
        return CalendarWeek.month_names(loc)
    except locale.Error:
        return CalendarWeek.month_names()


def i18n_month_abbrs(loc: Optional[str] = None) -> Tuple[str]:
    """ Return a tuple of month name abbreviations for the current locale. """

    if loc is None:
        loc = to_locale(get_language() or settings.LANGUAGE_CODE)

    try:
        return CalendarWeek.month_abbrs(loc)
    except locale.Error:
        return CalendarWeek.month_abbrs()


def i18n_day_name_choices(loc: Optional[str] = None) -> Tuple[Tuple[int, str]]:
    """ Return an enumeration of day names for the current locale. """

    return list(enumerate(i18n_day_names(loc)))


def i18n_day_abbr_choices(loc: Optional[str] = None) -> Tuple[Tuple[int, str]]:
    """ Return an enumeration of day name abbreviations for the current locale. """

    return list(enumerate(i18n_day_abbrs(loc)))


def i18n_month_name_choices(loc: Optional[str] = None) -> Tuple[Tuple[int, str]]:
    """ Return an enumeration of month names for the current locale. """

    return list(enumerate(i18n_month_names(loc)))


def i18n_month_abbr_choices(loc: Optional[str] = None) -> Tuple[Tuple[int, str]]:
    """ Return an enumeration of month name abbreviations for the current locale. """

    return list(enumerate(i18n_month_abbrs(loc)))


def i18n_js(request: HttpRequest) -> HttpResponse:
    """ Deliver a JS file containing JS representations of the current locale's
    calendar translations. """

    # Begin day names at this element
    # 0 (default = Monday, 6 = Sunday
    first_day = int(request.GET.get("first_day", "0"))
    day_indices = list(range(first_day, 7)) + list(range(0, first_day))
    def reorder(l: List[Any], i: List[int]) -> List[Any]:
        return [l[n] for n in i]

    # Get locale from request; can also be used to control caching
    loc = request.GET.get("locale", None)

    return HttpResponse(
        "var calendarweek_i18n = "
        + json.dumps(
            {
                "day_names": reorder(i18n_day_names(loc), day_indices),
                "day_abbrs": reorder(i18n_day_abbrs(loc), day_indices),
                "month_names": i18n_month_names(loc),
                "month_abbrs": i18n_month_abbrs(loc),
            }
        ),
        content_type="text/javascript",
    )


i18n_day_names_lazy = lazy(i18n_day_names, tuple)
i18n_day_abbrs_lazy = lazy(i18n_day_abbrs, tuple)
i18n_day_name_choices_lazy = lazy(i18n_day_name_choices, tuple)
i18n_day_abbr_choices_lazy = lazy(i18n_day_abbr_choices, tuple)
i18n_month_names_lazy = lazy(i18n_month_names, tuple)
i18n_month_abbrs_lazy = lazy(i18n_month_abbrs, tuple)
i18n_month_name_choices_lazy = lazy(i18n_month_name_choices, tuple)
i18n_month_abbr_choices_lazy = lazy(i18n_month_abbr_choices, tuple)
