from assertman.assertable_mixin import AssertableMixin
from assertman import objects
from assertman.helpers import jsonpath_helper


class AssertableList(list, AssertableMixin):
    _assertion_processing = "hamcrest"

    def __getitem__(self, key):
        obj = objects.make_assertable_object(super(AssertableList, self).__getitem__(key))
        obj._assertion_processing = "hamcrest"
        return obj

    @property
    def _assertable_data(self):
        return self

    def filter(self, *args, **kwargs):
        """
        Отфильтровать проверяемый документ-список, оставив только то, что подходит под переданные условия

        :param args: условия фильтрации в виде функции или JsonPatch
        :param kwargs: условия фильтрации в виде key-value аргументов
        :return: AssertableList
        """
        if not isinstance(self._assertable_data, list):
            raise ValueError("Операция доступна только для списков")

        # для пустого списка любая фильтрация вернет пустой список
        if len(self._assertable_data) == 0:
            result = self._assertable_data

        else:
            if len(args) != 0:
                if len(args) > 1:
                    raise ValueError("В виде функции может быть передана только одно условие")

                # если передано условие фильтрации в виде функции
                if callable(args[0]):
                    result = list(filter(args[0], self._assertable_data))

                # если передано условие фильтрации в виде JsonPatch
                elif isinstance(args[0], str) and args[0].startswith('$'):
                    result = jsonpath_helper.match(args[0], self._assertable_data)
                else:
                    raise ValueError("Переданное условие не является ни функцией, ни JsonPatch")

            # если передано условие фильтрации в виде key-value значений
            elif kwargs:
                # в этом случае список должен содержать только словари
                if not isinstance(self._assertable_data[0], dict):
                    raise ValueError("Если условиее задано как key-value, то элементы списка должны быть словарем")

                result = []
                for key, value in kwargs.items():
                    result = [item for item in self._assertable_data if item.get(key) == value]

            # если условие фильтрации не передано, то фильтрации не произойдет
            else:
                result = self._assertable_data

        obj = objects.make_assertable_object(result)
        obj._assertion_processing = "hamcrest"
        return obj

    def find(self, *args, **kwargs):
        """Найти в проверяемом документе-списке подходящую под условия запись и вернуть ее

        :param args: условия фильтрации в виде функции или JSONPath
        :param kwargs: условия фильтрации в виде key-value аргументов
        :return: AssertableList
        """

        # для пустого списка поиск невозможен, поэтому вернется ошибка
        if len(self._assertable_data) == 0:
            raise AssertionError('Не удается выполнить поиск в пустом списке')

        result = self.filter(*args, **kwargs)

        if len(result) > 1:
            raise AssertionError('Под заданные условия поиска найдено более одного элемента')

        if len(result) == 0:
            raise AssertionError('Под заданные условия поиска не найдено ни одного элемента')

        obj = objects.make_assertable_object(result[0])
        obj._assertion_processing = "hamcrest"
        return obj
