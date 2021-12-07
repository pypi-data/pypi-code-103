import pytest
from assertman.assert_that import that
from assertman.matchers import *

from assertman.objects import AssertableList

my_simple_list = my_list = [1000, 1500, 2000]

my_list_with_dicts = [
    {"id": 123, "age": 2020, "name": "Довод", "country": "USA"},
    {"id": 234, "age": 2010, "name": "Матрица", "country": "USA"},
    {"id": 345, "age": 1986, "name": "Назад в будущее", "country": "USA"}
]


def test_raises_when_assertable_document_is_not_list():
    """Если проверяемый объект не список, то поиск недоступен."""
    with pytest.raises(NotImplementedError) as execinfo:
        assert that({"price": 15}).find(lambda x: x > 1200)

    assert str(execinfo.value) == 'Поиск элемента доступен только для списков'


def test_raises_when_found_more_than_one_item():
    """Если в результате поиска найдено больше чем один подходящий под условия элемент, то выбрасывается ошибка"""
    with pytest.raises(AssertionError) as execinfo:
        assert that(my_simple_list).find(lambda x: x > 1200)

    assert str(execinfo.value) == 'Под заданные условия поиска найдено более одного элемента'


def test_empty_list():
    """Для пустого списка выбрасывается ошибка"""
    with pytest.raises(AssertionError) as execinfo:
        assert that([]).find(lambda x: x > 1200)

    assert str(execinfo.value) == 'Не удается выполнить поиск в пустом списке'


class TestListFindWithFunction:
    """Поиск, когда условие поиска - функция"""

    my_list = [1000, 1500, 2000]

    def test_positive_1(self):
        """Тест использования поиска (простой вариант)"""
        result = that(my_simple_list).find(lambda x: x > 1700)
        assert result == 2000
        assert result.should(equal_to(2000))

    def test_positive_2(self):
        """Тест использования поиска (вариант со вложенными словарями)"""
        result = that(my_list_with_dicts).find(lambda x: x['age'] < 2000)
        assert result == {"id": 345, "age": 1986, "name": "Назад в будущее", "country": "USA"}
        assert result.should(has_entries(id=345, name="Назад в будущее"))

    def test_raise_if_not_match(self):
        """Если под условия поиска не подошло ни одного элемента, выкидывается AssertionError."""
        with pytest.raises(AssertionError) as execinfo:
            assert that(my_list_with_dicts).find(lambda x: x['age'] > 3000)

        assert str(execinfo.value) == 'Под заданные условия поиска не найдено ни одного элемента'


class TestListFindWithKeyValue:
    """Фильтрация, когда условие поиска - key-value значение"""

    def test_positive(self):
        """Тест использования поиска"""
        result = that(my_list_with_dicts).find(country="USA", age=1986)
        assert result == {"id": 345, "age": 1986, "name": "Назад в будущее", "country": "USA"}
        assert result.should(has_entries(id=345, name="Назад в будущее"))

    def test_raise_if_not_match(self):
        """Если под условия поиска не подошло ни одного элемента, выкидывается AssertionError."""
        with pytest.raises(AssertionError) as execinfo:
            assert that(my_list_with_dicts).find(country="China", population=453245324534)

        assert str(execinfo.value) == 'Под заданные условия поиска не найдено ни одного элемента'


class TestListFindWithJsonPatch:
    """Фильтрация, когда условие фильтрации - JsonPatch"""


    @pytest.mark.parametrize("query, matcher1, matcher2", [
        ('$[0]', my_list_with_dicts[0], has_entries(id=123, name="Довод")),
        ('$[?id > 300]', my_list_with_dicts[2], has_entries(id=345, name="Назад в будущее")),
        ('$[1].age', my_list_with_dicts[1]["age"], equal_to(2010)),
    ])
    def test_positive(self, query, matcher1, matcher2):
        """Тест использования поиска"""
        result = that(my_list_with_dicts).find(query)
        assert result == matcher1
        assert result.should(matcher2)

    def test_raise_if_more_that_one_match(self):
        """Тест использования поиска"""
        with pytest.raises(AssertionError) as execinfo:
            assert that(my_list_with_dicts).find('$[0:2]')
        assert str(execinfo.value) == 'Под заданные условия поиска найдено более одного элемента'

    def test_raise_if_not_match(self):
        """Если под условия поиска не подошло ни одного элемента, выкидывается AssertionError."""
        with pytest.raises(AssertionError) as execinfo:
            assert that(my_list_with_dicts).find('$[7]')
        assert str(execinfo.value) == 'Под заданные условия поиска не найдено ни одного элемента'
