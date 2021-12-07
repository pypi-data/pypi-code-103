import pytest
from assertman.assert_that import that
from assertman.matchers import *


data = {
    "address": "naist street",
    "city": "Nara",
    "code": 630
}


# ------- has_key

def test_has_key():
    assert that(data).should(has_key('code'))


def test_not_has_key():
    assert that(data).should(not_(has_key('man')))


def test_raises_has_key():
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_key('man'))


def test_raises_not_has_key():
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(not_(has_key('code')))


# ------- has_entries

def test_has_has_entries():
    assert that(data).should(has_entries(city="Nara", code=630))


def test_not_has_entries():
    assert that(data).should(not_(has_entries(city="Nara", code=100)))


def test_raises_has_entries():
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_entries(city="Nara", code=100))


def test_raises_not_has_entries():
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(not_(has_entries(city="Nara", code=630)))