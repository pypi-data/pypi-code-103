import pytest
from assertman.assert_that import that
from assertman.matchers import *

from  assertman.objects import AssertableList

my_list = [1000, 1500, 2000]


def test_positive():
    """Тест получения элемента списка по индексу"""
    assert that([1000, 1500, 2000])[0].should(equal_to(1000))


def test_raise_with_index_error():
    """Тест выдачи ошибки IndexError если элемента с запрошенным индексом нет в списке"""
    with pytest.raises(IndexError) as execinfo:
        assert that([1000, 1500, 2000])[8].should(equal_to(1000))



