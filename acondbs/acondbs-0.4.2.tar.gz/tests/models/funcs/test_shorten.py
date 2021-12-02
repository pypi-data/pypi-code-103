import pytest

from acondbs.models.funcs import shorten


params = [
    ("0123456789", dict(width=0), "..."),
    ("0123456789", dict(width=1), "..."),
    ("0123456789", dict(width=2), "..."),
    ("0123456789", dict(width=3), "..."),
    ("0123456789", dict(width=4), "0..."),
    ("0123456789", dict(width=5), "01..."),
    ("0123456789", dict(width=6), "012..."),
    ("0123456789", dict(width=7), "0123..."),
    ("0123456789", dict(width=8), "01234..."),
    ("0123456789", dict(width=9), "012345..."),
    ("0123456789", dict(width=10), "0123456789"),
    ("0123456789", dict(width=11), "0123456789"),
    ("0123456789", dict(width=12), "0123456789"),
    ("0123456789", dict(width=0, end=True), "..."),
    ("0123456789", dict(width=1, end=True), "..."),
    ("0123456789", dict(width=2, end=True), "..."),
    ("0123456789", dict(width=3, end=True), "..."),
    ("0123456789", dict(width=4, end=True), "...9"),
    ("0123456789", dict(width=5, end=True), "...89"),
    ("0123456789", dict(width=6, end=True), "...789"),
    ("0123456789", dict(width=7, end=True), "...6789"),
    ("0123456789", dict(width=8, end=True), "...56789"),
    ("0123456789", dict(width=9, end=True), "...456789"),
    ("0123456789", dict(width=10, end=True), "0123456789"),
    ("0123456789", dict(width=11, end=True), "0123456789"),
    ("0123456789", dict(width=12, end=True), "0123456789"),
    ("", dict(width=0), ""),
    ("", dict(width=1), ""),
    ("", dict(width=2), ""),
    ("", dict(width=3), ""),
    ("", dict(width=4), ""),
    ("", dict(width=0, end=True), ""),
    ("", dict(width=1, end=True), ""),
    ("", dict(width=2, end=True), ""),
    ("", dict(width=3, end=True), ""),
    ("", dict(width=4, end=True), ""),
]


@pytest.mark.parametrize("text, kwargs, expected", params)
def test_func(text, kwargs, expected):
    assert shorten(text, **kwargs) == expected
