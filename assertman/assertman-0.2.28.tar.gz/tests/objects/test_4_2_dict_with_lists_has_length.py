import pytest
from assertman.assert_that import that
from assertman.matchers import *


data = {
    "cities": [
        {"name": "Moscow", "year": 1147, "is_capital": True},
        {"name": "London", "year": 47, "is_capital": True},
        {"name": "NewYork", "year": 1603, "is_capital": True}
    ],
}


# ------- has_length

def test_has_length():
    assert that(data).should(has_entries(
        cities=has_length(3)
    ))


def test_has_length_less_than():
    assert that(data).should(has_entries(
        cities=has_length(less_than(4))
    ))


def test_raises_has_length():
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_entries(
            cities=has_length(2)
        ))
