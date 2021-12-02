import csv

import pytest

##__________________________________________________________________||
multiline_entry = """\
"abc
xyz",def,ghi\
"""

params = [
    pytest.param(
        ("abc,def,ghi",),
        [["abc", "def", "ghi"]],
        id="simple",
    ),
    pytest.param(
        ('"abc",def,ghi',),
        [["abc", "def", "ghi"]],
        id="double-quotes-removed",
    ),
    pytest.param(
        ("'abc',def,ghi",),
        [["'abc'", "def", "ghi"]],
        id="single-quotes-not-removed",
    ),
    pytest.param(
        ('"""abc",def,ghi',),
        [['"abc', "def", "ghi"]],
        id="to-include-double-quote",
    ),
    pytest.param(
        ('"ab,c",def,ghi',),
        [["ab,c", "def", "ghi"]],
        id="to-include-comma",
    ),
    pytest.param(
        (multiline_entry,),
        [["abc\nxyz", "def", "ghi"]],
        id="to-include-linebreak",
    ),
]


@pytest.mark.parametrize("input, expected", params)
def test_csv_specification(input, expected):
    """test CSV specification

    This test is used to check the CSV specification as implemented in
    csv.reader(), in particular, to understand how quotes are treated
    and how to include double quotes, commas, and line breaks in data

    """
    rows = list(csv.reader(input))
    assert expected == rows


##__________________________________________________________________||
