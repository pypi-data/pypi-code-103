import pytest
from assertman.assert_that import that
from assertman.matchers import *


data = [
    {
        "type": "work",
        "number": 123
    },
    {
        "type": "home",
        "number": 124
    }
]


# ------- has_length

def test_has_length():
    assert that(data).should(has_length(2))


def test_has_length_greater_than():
    assert that(data).should(has_length(greater_than(1)))


def test_raise_has_length():
    with pytest.raises(AssertionError) as excinfo:
        assert that(['первый', 'второй', 'третий']).should(has_length(5))


# ------- has_item

def test_has_item():
    assert that(data).should(has_item({"type": "work", "number": 123}))


def test_not_has_item():
    assert that(data).should(not_(has_item({"type": "market", "number": 123})))


def test_raise_has_item():
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_item({"type": "market", "number": 123}))


def test_raise_not_has_item():
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(not_(has_item({"type": "work", "number": 123})))


# ------- has_items

def test_has_items():
    assert that(data).should(has_items(
        {"type": "work", "number": 123},
        {"type": "home", "number": 124}
    ))


def test_not_has_items():
    assert that(data).should(not_(has_items(
        {"type": "market", "number": 123},
        {"type": "bank", "number": 124}
    )))


def test_raise_has_items():
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(has_items(
            {"type": "bank", "number": 123},
            {"type": "market", "number": 124}
        ))


def test_raise_not_has_items():
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(not_(has_items(
            {"type": "work", "number": 123},
            {"type": "home", "number": 124}
        )))


# ------- every_item

def test_every_item():
    assert that(data).should(every_item(has_key("number")))


def test_raise_every_item():
    with pytest.raises(AssertionError) as excinfo:
        assert that(data).should(every_item(has_key("age")))

