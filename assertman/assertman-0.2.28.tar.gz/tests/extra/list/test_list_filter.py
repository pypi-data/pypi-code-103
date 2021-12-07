import pytest
from assertman.assert_that import that
from assertman.matchers import *



my_simple_list = [1000, 1500, 2000]

my_list_with_dicts = [
    {"id": 123, "age": 2020, "name": "Довод", "country": "USA"},
    {"id": 234, "age": 2010, "name": "Матрица", "country": "USA"},
    {"id": 345, "age": 1986, "name": "Назад в будущее", "country": "USA"}
]

def test_raises_when_assertable_document_is_not_list():
    """Если проверяемый объект не список, то фильтрация недоступна."""
    with pytest.raises(NotImplementedError) as execinfo:
        assert that({"price": 15}).filter(lambda x: x > 1200)

    assert str(execinfo.value) == 'Фильтрация доступна только для списков'


def test_empty_list():
    """Для пустого списка фильтрация вернет пустой список"""
    result = that([]).filter(lambda x: x > 1200)
    assert result == []


class TestListFilterWithFunction:
    """Фильтрация, когда условие фильтрации - функция"""

    my_list = [1000, 1500, 2000]

    def test_positive_1(self):
        """Тест использования фильтрации (простой вариант)"""
        result = that(my_simple_list).filter(lambda x: x > 1200)
        assert result == [1500, 2000]
        assert result.should(has_length(2))

    def test_positive_2(self):
        """Тест использования фильтрации (вариант со вложенными словарями)"""
        result = that(my_list_with_dicts).filter(lambda x: x['age'] > 2000)
        assert result == [
            {"id": 123, "age": 2020, "name": "Довод", "country": "USA"},
            {"id": 234, "age": 2010, "name": "Матрица", "country": "USA"}
        ]
        assert result.should(has_item(has_entries(id=123, name="Довод")))
        assert result.should(has_item(has_entries(id=234, name="Матрица")))

    def test_return_empty_list_if_not_match(self):
        """Если по условию фильтрации не найдено ничего, то вернется пустой список"""
        result = that(my_list_with_dicts).filter(lambda x: x['age'] > 3000)
        assert result == []
        assert result.should(has_length(0))

    def test_raises_when_filter_arg_not_function(self):
        """Передаваемое условие фильтрации должно быть функцией"""
        with pytest.raises(ValueError) as execinfo:
            assert that(my_simple_list).filter(greater_than(1100))

        assert str(execinfo.value) == 'Переданное условие не является ни функцией, ни JsonPatch'

    def test_raises_when_filter_has_more_one_arg(self):
        """Может быть передана только одно условие фильтрации в виде функции"""
        with pytest.raises(ValueError) as execinfo:
            assert that(my_simple_list).filter(lambda x: x > 1200, lambda x: x < 1800)

        assert str(execinfo.value) == 'В виде функции может быть передана только одно условие'


class TestListFilterWithKeyValue:
    """Фильтрация, когда условие фильтрации - key-value значение"""

    def test_positive(self):
        """Тест использования фильтрации"""
        result = that(my_list_with_dicts).filter(country="USA", age=1986)
        assert result == [
            {"id": 345, "age": 1986, "name": "Назад в будущее", "country": "USA"}
        ]
        assert result.should(has_item(has_entries(id=345, name="Назад в будущее")))

    def test_return_empty_list_if_not_match(self):
        """Если по условию фильтрации не найдено ничего, то вернется пустой список"""
        result = that(my_list_with_dicts).filter(city="Moscow", population=50000)
        assert result == []
        assert result.should(has_length(0))

    def test_raises_when_list_not_has_dicts(self):
        """Если условиее задано как key-value, то элементы списка должны быть словарем"""
        with pytest.raises(ValueError) as execinfo:
            assert that(my_simple_list).filter(country="USA", age=1986)

        assert str(execinfo.value) == 'Если условиее задано как key-value, то элементы списка должны быть словарем'


class TestListFilterWithJsonPatch:
    """Фильтрация, когда условие фильтрации - JsonPatch"""

    @pytest.mark.parametrize("query, matcher1, matcher2", [
        ('$[0]', [my_list_with_dicts[0]], has_length(1)),
        ('$[0:2]', my_list_with_dicts[0:2], has_length(2)),
        ('$[?id > 300]', [my_list_with_dicts[2]], has_length(1)),
        ('$[*].age', [i["age"] for i in my_list_with_dicts], has_length(3)),
    ])
    def test_positive(self, query, matcher1, matcher2):
        """Тест использования фильтрации"""
        result = that(my_list_with_dicts).filter(query)
        assert result == matcher1
        assert result.should(matcher2)

    def test_return_empty_list_if_not_match(self):
        """Если по условию фильтрации ничего не найдено, то вернется пустой список"""
        result = that(my_list_with_dicts).filter('$[7]')
        assert result == []
        assert result.should(has_length(0))




ddd = [
    {"id": 234, "age": 2010, "name": "Матрица"},
    {"id": 345, "age": 1986, "name": "Назад в будущее"}
]

def test_werqwer():
    assert that(ddd)\
        .filter('$[?id > 300]')\
        .should(equal_to([{"id": 345, "age": 1986, "name": "Назад в будущее"}]))

