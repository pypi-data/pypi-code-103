##############################################################################
# Copyright 2009, Gerhard Weis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT
##############################################################################
"""
Test cases for the isodate module.
"""
from datetime import date

import pytest

from isodate import (
    DATE_BAS_COMPLETE,
    DATE_BAS_MONTH,
    DATE_BAS_ORD_COMPLETE,
    DATE_BAS_WEEK,
    DATE_BAS_WEEK_COMPLETE,
    DATE_CENTURY,
    DATE_EXT_COMPLETE,
    DATE_EXT_MONTH,
    DATE_EXT_ORD_COMPLETE,
    DATE_EXT_WEEK,
    DATE_EXT_WEEK_COMPLETE,
    DATE_YEAR,
    ISO8601Error,
    date_isoformat,
    parse_date,
)

# the following list contains tuples of ISO date strings and the expected
# result from the parse_date method. A result of None means an ISO8601Error
# is expected. The test cases are grouped into dates with 4 digit years
# and 6 digit years.
TEST_CASES = [
    (4, "19", date(1901, 1, 1), DATE_CENTURY),
    (4, "1985", date(1985, 1, 1), DATE_YEAR),
    (4, "1985-04", date(1985, 4, 1), DATE_EXT_MONTH),
    (4, "198504", date(1985, 4, 1), DATE_BAS_MONTH),
    (4, "1985-04-12", date(1985, 4, 12), DATE_EXT_COMPLETE),
    (4, "19850412", date(1985, 4, 12), DATE_BAS_COMPLETE),
    (4, "1985102", date(1985, 4, 12), DATE_BAS_ORD_COMPLETE),
    (4, "1985-102", date(1985, 4, 12), DATE_EXT_ORD_COMPLETE),
    (4, "1985W155", date(1985, 4, 12), DATE_BAS_WEEK_COMPLETE),
    (4, "1985-W15-5", date(1985, 4, 12), DATE_EXT_WEEK_COMPLETE),
    (4, "1985W15", date(1985, 4, 8), DATE_BAS_WEEK),
    (4, "1985-W15", date(1985, 4, 8), DATE_EXT_WEEK),
    (4, "1989-W15", date(1989, 4, 10), DATE_EXT_WEEK),
    (4, "1989-W15-5", date(1989, 4, 14), DATE_EXT_WEEK_COMPLETE),
    (4, "1-W1-1", None, DATE_BAS_WEEK_COMPLETE),
    (6, "+0019", date(1901, 1, 1), DATE_CENTURY),
    (6, "+001985", date(1985, 1, 1), DATE_YEAR),
    (6, "+001985-04", date(1985, 4, 1), DATE_EXT_MONTH),
    (6, "+001985-04-12", date(1985, 4, 12), DATE_EXT_COMPLETE),
    (6, "+0019850412", date(1985, 4, 12), DATE_BAS_COMPLETE),
    (6, "+001985102", date(1985, 4, 12), DATE_BAS_ORD_COMPLETE),
    (6, "+001985-102", date(1985, 4, 12), DATE_EXT_ORD_COMPLETE),
    (6, "+001985W155", date(1985, 4, 12), DATE_BAS_WEEK_COMPLETE),
    (6, "+001985-W15-5", date(1985, 4, 12), DATE_EXT_WEEK_COMPLETE),
    (6, "+001985W15", date(1985, 4, 8), DATE_BAS_WEEK),
    (6, "+001985-W15", date(1985, 4, 8), DATE_EXT_WEEK),
]


@pytest.mark.parametrize("year_digits, date_string, expectation, format", TEST_CASES)
def test_parse(year_digits, date_string, expectation, format):
    """
    Parse an ISO date string and compare it to the expected value.
    """
    if expectation is None:
        with pytest.raises(ISO8601Error):
            parse_date(date_string, year_digits)
    else:
        result = parse_date(date_string, year_digits)
        assert result == expectation


@pytest.mark.parametrize("year_digits, date_string, expectation, format", TEST_CASES)
def test_format(year_digits, date_string, expectation, format):
    """
    Take date object and create ISO string from it.
    This is the reverse test to test_parse.
    """
    if expectation is None:
        with pytest.raises(AttributeError):
            date_isoformat(expectation, format, year_digits)
    else:
        result = date_isoformat(expectation, format, year_digits)
        assert result == date_string
