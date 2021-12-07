import pytest
from assertman.assert_that import that
from assertman.matchers import *


my_dict = {
    "info":
        {"age": 2020, "name": "Довод"}
}


def test_raises_when_assertable_document_is_not_dict():
    """Если проверяемый объект не словарь, то фильтрация недоступна."""
    with pytest.raises(NotImplementedError) as execinfo:
        assert that([1, 2]).extract('info')

    assert str(execinfo.value) == 'Извлечение по ключу доступно только для словарей'


def test_positive_1():
    """Тест использования извлечения (вариант с extract)"""
    result = that(my_dict).extract('info')
    assert result == {"age": 2020, "name": "Довод"}
    assert result.should(has_entries(age=2020, name="Довод"))


def test_positive_2():
    """Тест использования извлечения (вариант с [])"""
    result = that(my_dict)['info']
    assert result == {"age": 2020, "name": "Довод"}
    assert result.should(has_entries(age=2020, name="Довод"))


def test_raises_when_dict_not_have_extracting_key():
    """Если извлекаемый ключ не найден в словаре, выдается сообщение об ошибке"""
    with pytest.raises(AssertionError) as execinfo:
        assert that(my_dict).extract('items')

    assert str(execinfo.value) == 'Ключ <items> не найден в словаре'


