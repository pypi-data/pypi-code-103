import hamcrest
from hamcrest.core.base_matcher import BaseMatcher
from assertman import cerberus_wrapper


__tracebackhide__ = True


class AssertableMixin:

    _assertion_processing = None

    @property
    def _assertable_data(self):
        raise NotImplementedError(
            'Что бы добавить объекту свойство `assertable`, определите в нем метод `_assertable_data`')

    def should(self, matcher):
        if not isinstance(matcher, BaseMatcher):
            raise TypeError(f'Переданный матчер имеет неподдерживаемый тип {type(matcher)}')

        if type(matcher).__name__ in ['IsDictContainingEntries']:
            cerberus_wrapper.assert_that(self._assertable_data, matcher)
        else:
            hamcrest.assert_that(self._assertable_data, matcher)
        return True

    def filter(self, *args, **kwargs):
        raise NotImplementedError("Фильтрация доступна только для списков")

    def find(self, *args, **kwargs):
        raise NotImplementedError("Поиск элемента доступен только для списков")

    def extract(self, query):
        raise NotImplementedError("Извлечение по ключу доступно только для словарей")

