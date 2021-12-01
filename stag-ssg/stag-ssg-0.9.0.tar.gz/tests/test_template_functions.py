import pytest

from stag.ecs import Page, Metadata, Path
from stag.writers.template_functions import sorted_pages, sortby


class Foo:
    def __init__(self, **kw):
        for name, val in kw.items():
            setattr(self, name, val)


@pytest.fixture
def files():
    return [
        Page("/static.txt"),
        Page("/bar", metadata=Metadata(date="2021-08-09")),
        Page("/empty", metadata=Metadata()),
        Page("/foo", metadata=Metadata(date="2021-08-10")),
        Page("/baz", metadata=Metadata(date="2020-11-11")),
    ]


@pytest.fixture
def pages():
    return [
        Page("/3", metadata=Metadata(a=3)),
        Page("/1", metadata=Metadata(a=1)),
        Page("/None"),
        Page("/0", metadata=Metadata(a=0)),
        Page("/2", metadata=Metadata(a=2)),
    ]


def test_sort_default_key(files):
    srt = sorted_pages(files)
    assert srt == [files[1], files[4], files[2], files[3], files[0]]


def test_sort_default_key_reverse(files):
    srt = sorted_pages(files, reverse=True)
    assert srt == [files[0], files[3], files[2], files[4], files[1]]


def test_sort_date(files):
    srt = sorted_pages(files, key="date")
    assert srt[0] == files[4]
    assert srt[1] == files[1]
    assert srt[2] == files[3]
    # last 2 elements don't have date, so they are considered equal and their
    # order is undefined


def test_sort_date_reverse(files):
    srt = sorted_pages(files, key="date", reverse=True)
    # first 2 elements don't have date, so they are considered equal and their
    # order is undefined
    assert srt[2] == files[3]
    assert srt[3] == files[1]
    assert srt[4] == files[4]


def test_sortby(pages):
    srt = sortby(pages, "md.a", default=100)
    assert srt == [pages[i] for i in (3, 1, 4, 0, 2)]


def test_sortby_reversed(pages):
    srt = sortby(pages, "md.a", default=-1, reverse=True)
    assert srt == [pages[i] for i in (0, 4, 1, 3, 2)]


def test_sortby_many_attrs():
    pages = [
        Page("/33", metadata=Metadata(a=3, b=3)),
        Page("/3None", metadata=Metadata(a=3)),
        Page("/31", metadata=Metadata(a=3, b=1)),
    ]

    srt = sortby(pages, "md.a", "md.b", default=[0, 0])
    assert srt == [pages[i] for i in (1, 2, 0)]
