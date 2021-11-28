# pylint: skip-file
import pytest

from .. import matches


def test_list_matching_no_wilcard():
    patterns = ["foo"]
    values = ["foo", "bar", "baz", "baz.taz", "foo.bar"]
    assert matches(patterns, values) == {"foo"}


def test_list_matching_with_wilcard():
    patterns = ["foo", "bar.*"]
    values = ["foo", "bar", "baz", "bar.taz", "foo.bar"]
    assert matches(patterns, values) == {"foo", "bar.taz"}
