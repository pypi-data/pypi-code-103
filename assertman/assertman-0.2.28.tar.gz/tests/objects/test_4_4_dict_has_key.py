import pytest
from assertman.assert_that import that
from assertman.matchers import *


data = {
    "city": {
        "name": "Moscow",
        "year": 1147,
        "is_capital": True
    }
}


# ------- has_key

def test_has_key():
    """Позитивный тест"""
    assert that(data).should(has_entries(
        city=has_key("name")
    ))


def test_has_key_with_raises():
    """Срабатывание ассерта в позитивном тесте"""
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_entries(
            city=has_key("population")
        ))


def test_not_has_key():
    """Тест с отрицанием"""
    assert that(data).should(has_entries(
        city=not_(has_key("population"))
    ))


def test_not_has_key_with_raises():
    """Срабатывание ассерта в тесте с отрицанием"""
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_entries(
            city=not_(has_key("name"))
        ))



