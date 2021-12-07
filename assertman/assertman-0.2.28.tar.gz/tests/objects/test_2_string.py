import pytest
from assertman.assert_that import that
from assertman.matchers import *


def test_1():
    assert that('Назад в будущее').should(equal_to('Назад в будущее'))


def test_3():
    assert that('Назад в будущее').should(starts_with('Назад'))


def test_raises_1():
    with pytest.raises(TypeError) as excinfo:
        assert that(34).should(36)


def test_raises_2():
    with pytest.raises(AssertionError) as excinfo:
        assert that('Назад в будущее').should(equal_to('Назад в будущее!'))




