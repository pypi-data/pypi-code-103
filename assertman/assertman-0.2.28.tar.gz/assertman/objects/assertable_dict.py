from assertman import objects
from assertman.assertable_mixin import AssertableMixin
from assertman.helpers import jsonpath_helper


class AssertableDict(dict, AssertableMixin):
    _assertion_processing = "cerberus"

    def __getitem__(self, key):
        obj = objects.make_assertable_object(super(AssertableDict, self).__getitem__(key))
        obj._assertion_processing = "hamcrest"
        return obj

    @property
    def _assertable_data(self):
        return self

    def __call__(self, query):
        return self.__class__(self).extract(query)

    def extract(self, query):
        """Достать нужные данные из проверяемого документа-словаря по ключу или с использованием JSONPath.

        :param query: ключ словаря или JSONPath-селектор
        """
        if not isinstance(self._assertable_data, dict):
            raise NotImplementedError("Извлечение по ключу доступно только для словарей")

        if query.startswith('$'):
            # значит работаем через jsonpath
            result = jsonpath_helper.match_smart(query, self._assertable_data)
        else:
            # работаем через взятие значения по ключу
            if self._assertable_data.get(query) is None:
                raise AssertionError(f"Ключ <{query}> не найден в словаре")
            result = self._assertable_data[query]

        obj = objects.make_assertable_object(result)
        obj._assertion_processing = "hamcrest"
        return obj



