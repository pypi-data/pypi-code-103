import copy
from cerberus import Validator
from cerberus import errors
import operator
import typing
import hamcrest as matchers

from assertman import datetimes
from assertman.helpers.datetime_helper import DateTimeApi



class SkyrimValidator(Validator):
    """ Класс содержит кастомные или переопределенные правила валидации схемы cerberus

    Задача валидатора:
    1) выполнить проверку, любым доступным образом
    2) сформировать сообщение об ошибке и записать его в дерево ошибок, возникших при проверке схемы
    (используя метод `self._error()`)
    """

    def __is_inversion(self, matcher):
        return True if type(matcher).__name__ == 'CerberusNot' else False

    def __is_negative(self, matcher):
        """ Возвращает информацию, о том матчер какого типа передан: позитивный или с отрицанием
        Матчер с отрицанием, это тот который `not_()`
        """
        return True if type(matcher).__name__ == 'CerberusNot' else False

    def _unwrap(self, matcher):
        return (False, "not ", matcher.value) if self.__is_negative(matcher) else (True, "", matcher)

    def __hamcrest_assert_that(self, value, hamcrest_matcher):
        try:
            matchers.assert_that(value, hamcrest_matcher)
            return True
        except Exception as e:
            return False

    def _validate_equal_to(self, matcher, field, value):
        """ Реализация проверки того, что `value` равен `matcher`
        * проверка равенства реализована через `__eq__`
        * перед основной проверкой, проверяетcя соответствие типов объектов, и если они не равны,
        записывает более информативное сообщенниее об ошибке
        The rule's arguments are validated against this schema: {'nullable': True}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        # Временный костыль.
        # Что бы не было проблем со сравнением типов, достаем из AssertableBool его реальное значение
        if type(value).__name__ == 'AssertableBool':
            value = value.value

        # Проверка на соответствие типов сравниваемых элементов
        if matcher != None:

            if isinstance(value, bool) or isinstance(matcher, bool):
                if not (isinstance(value, type(matcher)) and isinstance(matcher, type(value))):
                    self._error(field, f"Type mismatch. Must be {not_}`{matcher}` ({type(matcher).__name__}), "
                                       f"but was `{value}` ({type(value).__name__})")
                    return


            elif not (isinstance(value, type(matcher))):
                self._error(field, f"Type mismatch. Must be {not_}`{matcher}` ({type(matcher).__name__}), "
                                      f"but was `{value}` ({type(value).__name__})")
                return

        # Проверка на равенство
        if (matcher == value) != expected_result:
            self._error(field, f"Must be {not_}`{matcher}`, but was `{value}`")

    # -------- Numbers ----------------------------------------------------------------

    def _validate_close_to(self, matcher, field, value):
        """ Реализация проверки того, что `value` отличается от `matcher` не более чем на `delta`
        * matcher - кортеж, первым элементом которого идет ожидаемое значение, а вторым дельта
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        matcher, delta = matcher
        if not self.__hamcrest_assert_that(value, matchers.close_to(matcher, delta)):
            self._error(field, f"Must be close to <{matcher}> with delta <{delta}>, "
                               f"but was <{value}> differed by <{value - matcher}>")

    def __validate_ordering_comparison(self, comparison_function, comparison_description, matcher, field, value):
        """ Вспомогательный метод сравнения чисел: >, >=, <, <= """
        if self.__is_negative(matcher):
            raise TypeError(f"Вместо матчера с отрицанием `not_({comparison_description.replace(' ', '_')}({matcher.value}))`, "
                            f"лучше использовать его антипод:"
                            f"\n\t- not_(greater_than({matcher.value})) -> less_than({matcher.value})"
                            f"\n\t- not_(less_than({matcher.value})) -> greater_than({matcher.value})"
                            f"\n\t- not_(greater_than_or_equal_to({matcher.value})) -> less_than_or_equal_to({matcher.value})"
                            f"\n\t- not_(less_than_or_equal_to({matcher.value})) -> greater_than_or_equal_to({matcher.value})")
        if not comparison_function(value, matcher):
            self._error(field, f"Must be {comparison_description} <{matcher}> but was <{value}>")

    def _validate_greater_than(self, matcher, field, value):
        """ Реализация проверки того, что `value` > `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        self.__validate_ordering_comparison(operator.gt, "greater than", matcher, field, value)

    def _validate_greater_than_or_equal_to(self, matcher, field, value):
        """ Реализация проверки того, что `value` >= `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        self.__validate_ordering_comparison(operator.ge, "greater than or equal to", matcher, field, value)

    def _validate_less_than(self, matcher, field, value):
        """ Реализация проверки того, что `value` < `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        self.__validate_ordering_comparison(operator.lt, "less than", matcher, field, value)

    def _validate_less_than_or_equal_to(self, matcher, field, value):
        """ Реализация проверки того, что `value` <= `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        self.__validate_ordering_comparison(operator.le, "less than or equal to", matcher, field, value)

    # -------- Text ----------------------------------------------------------------

    def _validate_contains_string(self, matcher, field, value):
        """ Реализация проверки того, что строка `value` содержит подстроку `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, matchers.contains_string(matcher)) != expected_result:
            self._error(field, f"Must be a string {not_}containing '{matcher}', but was '{value}'")

    def _validate_starts_with(self, matcher, field, value):
        """ Реализация проверки того, что строка `value` начинается с подстроки `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, matchers.starts_with(matcher)) != expected_result:
            self._error(field, f"Must be a string {not_}starts with '{matcher}', but was '{value}'")

    def _validate_ends_with(self, matcher, field, value):
        """ Реализация проверки того, что строка `value` начинается с подстроки `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, matchers.ends_with(matcher)) != expected_result:
            self._error(field, f"Must be a string {not_}ends with '{matcher}', but was '{value}'")

    def _validate_string_contains_in_order(self, matcher, field, value):
        """ Реализация проверки того, что строка `value` содержит в себе все строки из кортежа `matcher`,
        в том порядке - в котором они перечислены
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, matchers.string_contains_in_order(*matcher)) != expected_result:
            self._error(field, f"Must be a string {not_}containing {matcher} in order, but was '{value}'")

    def _validate_equal_to_ignoring_case(self, matcher, field, value):
        """ Реализация проверки того, что строка `value` равна строке `matcher` игнорируя регистр букв
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, matchers.equal_to_ignoring_case(matcher)) != expected_result:
            self._error(field, f"Must be a string {not_}equal to '{matcher}' ignoring case, but was '{value}'")

    # -------- List Length ----------------------------------------------------------------

    def _validate_length(self, matcher, field, value):
        """ Реализация проверки того, что длинна списка `value` равна числу `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, matchers.has_length(matcher)) != expected_result:
            self._error(field, f"Must has length {not_}<{matcher}>, but was length is <{len(value)}>. Object is: {value}")

    def _validate_minlength(self, matcher, field, value):
        """ Реализация проверки того, что длинна списка `value` >= `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        if isinstance(value, typing.Iterable) and len(value) < matcher:
            self._error(field, f"Must has minimum length <{matcher}>, but was length is <{len(value)}>. Object is: {value}")

    def _validate_maxlength(self, matcher, field, value):
        """ Реализация проверки того, что длинна списка `value` <= `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        if isinstance(value, typing.Iterable) and len(value) > matcher:
            self._error(field, f"Must has maximum length <{matcher}>, but was length is <{len(value)}>. Object is: {value}")

    # -------- Dict ---------------------------------------------------------------------------------------

    def _validate_has_key(self, matcher, field, value):
        """ Реализация проверки того, что словарь `value` содержит ключ `matcher`
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, matchers.has_key(matcher)) != expected_result:
            self._error(field, f"Must {not_}has key `{matcher}`, but was `{value}`")

    # -------- List: has_item / every_item ----------------------------------------------------------------

    def __validate_schema_custom_sequence(self, validation_type, field, schema, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """

        if isinstance(self.schema, dict):
            res = self.schema[field].pop(validation_type)
            self.schema[field].update({'schema': res})
        else:
            res = self.schema.schema[field].pop(validation_type)
            self.schema.schema[field].update({'schema': res})


        schema = dict(((i, schema) for i in range(len(value))))
        validator = self._get_child_validator(
            document_crumb=field,
            schema_crumb=(field, 'schema'),
            schema=schema,
            allow_unknown=self.allow_unknown,
        )
        validator(
            dict(((i, v) for i, v in enumerate(value))),
            update=self.update,
            normalize=False,
        )

        return validator

    def _validate_has_items(self, schema, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        self_schema = copy.deepcopy(self.schema)

        for index, item in enumerate(schema):
            if isinstance(self.schema, dict):
                res = self.schema[field].pop("has_items")
                self.schema[field].update({'schema': res})
            else:
                res = self.schema.schema[field].pop("has_items")[index]
                self.schema.schema[field].update({'schema': res})


            item = dict(((i, item) for i in range(len(value))))
            validator = self._get_child_validator(
                document_crumb=field,
                schema_crumb=(field, 'schema'),
                schema=item,
                allow_unknown=self.allow_unknown,
            )
            validator(
                dict(((i, v) for i, v in enumerate(value))),
                update=self.update,
                normalize=False,
            )

            if len(validator._errors) >= len(value):
                self._drop_nodes_from_errorpaths(validator._errors, [], [2])
                self._error(field, f"any item")
                self._error(field, errors.SEQUENCE_SCHEMA, validator._errors)
                break

            self.schema = copy.deepcopy(self_schema)

    def _validate_has_item(self, schema, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """

        validator = self.__validate_schema_custom_sequence("has_item", field, schema, value)

        if len(validator._errors) >= len(value):
            self._drop_nodes_from_errorpaths(validator._errors, [], [2])
            self._error(field, f"any item")
            self._error(field, errors.SEQUENCE_SCHEMA, validator._errors)

    def _validate_has_item_at_index(self, schema, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        index, schema = schema

        try:
            value[index]
        except IndexError:  # если в  последовательности нет элемента под запрошенным индексом
            self._error(field, f"В списке нет элемента с индексом: {index}. Длинна списка {len(value)}")
        else:
            validator = self.__validate_schema_custom_sequence("has_item_at_index", field, schema, value)

            # Может быть получен как положительнный, так и отрицательный индекс
            _positive_index = (len(value) + index) if index < 0 else index

            # error_for_index = [i for i in validator._errors if i.field == _positive_index]
            validator._errors = [i for i in validator._errors if i.field == _positive_index]
            if len(validator._errors) != 0:
                self._drop_nodes_from_errorpaths(validator._errors, [], [2])
                self._error(field, f"item at index={index}:")
                self._error(field, errors.SEQUENCE_SCHEMA, validator._errors)


    def _validate_every_item(self, schema, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """

        validator = self.__validate_schema_custom_sequence("every_item", field, schema, value)

        if validator._errors:
            self._drop_nodes_from_errorpaths(validator._errors, [], [2])
            self._error(field, f"all items  Всего элементов в списке {len(value)}, не удовлетовряют матчеру {len(validator._errors)}")
            self._error(field, errors.SEQUENCE_SCHEMA, validator._errors)

    # -------- Datetime ---------------------------------------------------------------------------------------

    def _validate_is_today_with_shift(self, matcher, field, value):
        """ Порт кастомных матчеров на основе хамкрестовских группы IsToday
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)
        message = matcher.get("message")
        if self.__hamcrest_assert_that(
                value, datetimes.is_today_with_shift(**{k: v for k, v in matcher.items() if k != "message"})) \
                != expected_result:
            self._error(field, f"Expected: {not_}{message}, "
                               f"but was: <{DateTimeApi(value).to_datetime_format()}>")

    def _validate_is_greater_than_datetime(self, matcher, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, datetimes.is_greater_than_datetime(matcher)) != expected_result:
            self._error(field, f"Must {not_}be greater "
                               f"than <{DateTimeApi(matcher).to_datetime_format()}>, "
                               f"but was: <{DateTimeApi(value).to_datetime_format()}> "
                               f"is {'not ' if not not_ else ''}greater")

    def _validate_is_less_than_datetime(self, matcher, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, datetimes.is_less_than_datetime(matcher)) != expected_result:
            self._error(field, f"Must {not_}be less "
                               f"than <{DateTimeApi(matcher).to_datetime_format()}>, "
                               f"but was: <{DateTimeApi(value).to_datetime_format()}> "
                               f"is {'not ' if not not_ else ''}less")

    def _validate_is_equal_to_datetime(self, matcher, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, datetimes.is_equal_to_datetime(matcher)) != expected_result:
            self._error(field, f"Must {not_}be equal to <{DateTimeApi(matcher).to_datetime_format()}>, "
                               f"but was: <{DateTimeApi(value).to_datetime_format()}>")

    def _validate_is_greater_than_date(self, matcher, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, datetimes.is_greater_than_date(matcher)) != expected_result:
            self._error(field, f"Must {not_}be greater "
                               f"than <{DateTimeApi(matcher).to_datetime_format()}>, "
                               f"but was: <{DateTimeApi(value).to_datetime_format()}> "
                               f"is {'not ' if not not_ else ''}greater (ignoring time)")

    def _validate_is_less_than_date(self, matcher, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, datetimes.is_less_than_date(matcher)) != expected_result:
            self._error(field, f"Must {not_}be less "
                               f"than <{DateTimeApi(matcher).to_datetime_format()}>, "
                               f"but was: <{DateTimeApi(value).to_datetime_format()}> "
                               f"is {'not ' if not not_ else ''}less (ignoring time)")

    def _validate_is_equal_to_date(self, matcher, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(value, datetimes.is_equal_to_date(matcher)) != expected_result:
            self._error(field, f"Must {not_}be equal to <{DateTimeApi(matcher).to_datetime_format()}>, "
                               f"but was: <{DateTimeApi(value).to_datetime_format()}> (ignoring time)")

    def _validate_is_equal_to_date_ignoring_seconds(self, matcher, field, value):
        """
        The rule's arguments are validated against this schema: {'nullable': False}
        """
        expected_result, not_, matcher = self._unwrap(matcher)

        if self.__hamcrest_assert_that(
                value, datetimes.close_to_datetime(matcher["value"], matcher["seconds"])) \
                != expected_result:
            self._error(field, f"Must {not_}be equal to <{DateTimeApi(matcher['value']).to_datetime_format()}>, "
                               f"but was: <{DateTimeApi(value).to_datetime_format()}> "
                               f"(ignoring {matcher['seconds']} seconds)")
