import pytest
from assertman.assert_that import that
from assertman.matchers import *


def test_1():
    assert that(34).should(equal_to(34))


def test_3():
    assert that(10).should(greater_than(5))


def test_raises_1():
    with pytest.raises(TypeError) as excinfo:
        assert that(34).should(36)


def test_raises_2():
    with pytest.raises(AssertionError) as excinfo:
        assert that(34).should(equal_to(36))

def test_raises_3():
    with pytest.raises(AssertionError) as excinfo:
        assert that(34).should(equal_to('34'))


