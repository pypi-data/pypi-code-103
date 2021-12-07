import pytest
from assertman.assert_that import that
from assertman.matchers import *


# ------- has_length


def test_has_length():
    assert that(['первый', 'второй', 'третий']).should(has_length(3))


def test_has_length_greater_than():
    assert that(['первый', 'второй', 'третий']).should(has_length(greater_than(2)))


def test_raise_has_length():
    with pytest.raises(AssertionError) as excinfo:
        assert that(['первый', 'второй', 'третий']).should(has_length(2))


def test_raise_has_length_greater_than():
    with pytest.raises(AssertionError) as excinfo:
        assert that(['первый', 'второй', 'третий']).should(has_length(greater_than(5)))


# ------- has_item

def test_has_item():
    assert that(['первый', 'второй', 'третий']).should(has_item('второй'))


def test_not_has_item():
    assert that(['первый', 'второй', 'третий']).should(not_(has_item('пятый')))


def test_raise_has_item():
    with pytest.raises(AssertionError) as excinfo:
        assert that(['первый', 'второй', 'третий']).should(has_item('пятый'))


def test_raise_not_has_item():
    with pytest.raises(AssertionError) as excinfo:
        assert that(['первый', 'второй', 'третий']).should(not_(has_item('второй')))


# ------- has_items

def test_has_items():
    assert that(['первый', 'второй', 'третий']).should(has_items('второй', 'третий'))


def test_not_has_items():
    assert that(['первый', 'второй', 'третий']).should(not_(has_items('пятый', 'шестой')))


def test_raise_has_items():
    with pytest.raises(AssertionError) as excinfo:
        assert that(['первый', 'второй', 'третий']).should(has_items('пятый', 'шестой'))


def test_raise_not_has_items():
    with pytest.raises(AssertionError) as excinfo:
        assert that(['первый', 'второй', 'третий']).should(not_(has_items('второй', 'третий')))


# ------- every_item

def test_every_item():
    assert that(['one one', 'one two', 'one three']).should(every_item(starts_with('one')))


def test_raise_every_item():
    with pytest.raises(AssertionError) as excinfo:
        assert that(['one one', 'one two', 'two three']).should(every_item(starts_with('one')))

# ------- ontains

def test_contains():
    assert that(['первый', 'второй', 'третий']).should(contains('первый', 'второй', 'третий'))


def test_raise_contains():
    with pytest.raises(AssertionError) as excinfo:
        assert that(['первый', 'второй', 'третий']).should(contains('пятый', 'второй', 'третий'))


# ------- empty

@pytest.mark.skip
def test_empty():
    assert that([]).should(empty())


def test_not_empty():
    assert that(['первый']).should(not_(empty()))


def test_raise_empty():
    with pytest.raises(AssertionError) as excinfo:
        assert that(['первый']).should(empty())


@pytest.mark.skip
def test_raise_not_empty():
    with pytest.raises(AssertionError) as excinfo:
        assert that([]).should(not_(empty()))
