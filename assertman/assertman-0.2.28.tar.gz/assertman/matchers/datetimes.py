from hamcrest.core.base_matcher import BaseMatcher
from assertman.helpers.datetime_helper import DateTimeApi


""" Библиотека кастомных матчеров для сравнения дат
    Сравнение доступно для дат в трех форматах: объект datetime, timestamp (str, int, float) и sdp
    Если хотя бы одно из сравниваемых значений не соответствует одному из этих форматов, возникает исключение

    Список проверок сразу с примерами:

    * assert_that(date1, is_equal_to_date_ignoring_seconds(date2, seconds=10)) # соответствие дат с погрешностью
                                                                               # в 10 секунд
                                                                               # можно не передавать параметр seconds
                                                                               # тогда по умолчанию погрешность 5 сек

    * assert_that(date, is_today()) # является ли дата сегодняшней без учета времени

    * assert_that(date, is_tomorrow()) # является ли дата завтрашней без учета времени

    * assert_that(date, is_yesterday()) # является ли дата вчерашней без учета времени

    * assert_that(date, is_today_with_shift(weeks=2, days=5)) # является ли дата сегодняшней без учета времени
                                                              # со сдвигом на 2 недели и 5 дней вперед
                                                              # можно задавать отрицательные значения - сдвиг назад
                                                              # можно передать только одно из этих значений
                                                              # если не передать значения - действует как is_today()

    * assert_that(date1, is_greater_than_date(date2)) # является ли date1 больше (позже) date2

    * assert_that(date1, is_less_than_date(date2)) # является ли date1 меньше (раньше) date2

    * assert_that(date1, is_equal_to_date(date2)) # равны ли даты date1 и date2 без учета миллисекунд

    * assert_that(value, is_date()) # является ли value датой в одном из доступных форматов:
                                    # SDP-дата, datetime, timestamp в int, float или str
"""




class DateComparison(BaseMatcher):
    """ Матчер сравнения дат """

    def __init__(self, date_time, operation, ignore_time=False, error_seconds=5):
        self.ignore_time = ignore_time
        self.operation = operation
        self.actual_item = date_time
        self.date_time = DateTimeApi(date_time)
        self.error1 = None
        self.error2 = None
        self.error_seconds = error_seconds
        self.expected_message = self._generate_expected_message()

    def _generate_expected_message(self):
        """ Метод генерирует первую часть сообщения об ошибке (там, где ожидаемая часть)
        """
        if self.operation == "greater":
            expected_message = "Actual date is greater than expected date" \
                if self.ignore_time else "Actual datetime is greater than expected date"
        elif self.operation == "less":
            expected_message = "Actual date is less than expected date" \
                if self.ignore_time else "Actual datetime is less than expected date"
        elif self.operation == "equal":
            expected_message = "Dates are equal" \
                if self.ignore_time else "Datetimes are equal"
        elif self.operation == "equal with error":
            expected_message = f"Dates are equal with margin of error in {self.error_seconds} seconds"
        else:
            raise ValueError("Данная операция не поддерживается матчером!")

        return expected_message

    def _matches(self, item):
        item = DateTimeApi(item)
        if not item.is_date():
            self.error1 = True
            return False

        if not self.date_time.is_date():
            self.error2 = True
            return False

        if self.operation == "greater":
            if self.ignore_time:
                return item.to_date_without_time() > self.date_time.to_date_without_time()
            else:
                return item.to_datetime_format() > self.date_time.to_datetime_format()
        elif self.operation == "less":
            return item.to_datetime_format() < self.date_time.to_datetime_format() \
                if not self.ignore_time \
                else item.to_date_without_time() < self.date_time.to_date_without_time()
        elif self.operation == "equal":
            return item.to_datetime_format() == self.date_time.to_datetime_format() \
                if not self.ignore_time \
                else item.to_date_without_time() == self.date_time.to_date_without_time()
        elif self.operation == "equal with error":
            return abs(item.to_timestamp_format() - self.date_time.to_timestamp_format()) <= self.error_seconds

    def describe_to(self, description):
        description.append_text(self.expected_message)

    def describe_mismatch(self, item, mismatch_description):
        if self.error1:
            mismatch_description.append_text(f"Value <{item}> does not match date format")
        elif self.error2:
            mismatch_description.append_text(f"Expected value <{self.actual_item}> does not match date format")
        else:
            item = DateTimeApi(item)
            # Для обратной совместимости с hamcrest-матчерами
            if self.operation == "equal with error":
                error_text = f"Actual date <{item.to_datetime_format()}> is not equal to " \
                             f"expected date <{self.date_time.to_datetime_format()}>"
            else:
                error_text = f"Actual date <{item.to_datetime_format()}> is not {self.operation} " \
                             f"{'to' if self.operation == 'equal' else 'than'} <{self.date_time.to_datetime_format()}>"

            mismatch_description.append_text(error_text)


def is_greater_than_datetime(date_time):
    """ Проверить, является ли проверяемая дата позже, чем переданная (с учетом времени, кроме миллисекунд)
    Пример использования:
    assert_that(date1, is_greater_than_datetime(date2))
    """
    return DateComparison(date_time=date_time, operation="greater")


def is_less_than_datetime(date_time):
    """ Проверить, является ли проверяемая дата раньше, чем переданная (с учетом времени, кроме миллисекунд)
    Пример использования:
    assert_that(date1, is_less_than_datetime(date2))
    """
    return DateComparison(date_time=date_time, operation="less")


def is_equal_to_datetime(date_time):
    """ Проверить даты на соответстие, исключая только миллисекунды
    Пример использования:
    assert_that(date1, is_equal_to_datetime(date2))
    """
    return DateComparison(date_time=date_time, operation="equal")


def is_greater_than_date(date_time):
    """ Проверить, является ли проверяемая дата позже, чем переданная (без учета времени)
    То есть например "03/05/2020 12:00:00" и "03/05/2020 14:59:00" равны без учета времени,
                      и в этом случае матчер вернет False
    Пример использования:
    assert_that(date1, is_greater_than_date(date2))
    """
    return DateComparison(date_time=date_time, operation="greater", ignore_time=True)


def is_less_than_date(date_time):
    """ Проверить, является ли проверяемая дата раньше, чем переданная (без учета времени)
    То есть например "03/05/2020 12:00:00" и "03/05/2020 14:59:00" равны без учета времени,
                      и в этом случае матчер вернет False
    Пример использования:
    assert_that(date1, is_less_than_date(date2))
    """
    return DateComparison(date_time=date_time, operation="less", ignore_time=True)


def is_equal_to_date(date_time):
    """ Проверить даты на соответстие (без учета времени)
    То есть например "03/05/2020 12:00:00" и "03/05/2020 14:59:00" равны без учета времени,
                      и в этом случае матчер вернет True
    Пример использования:
    assert_that(date1, is_equal_to_date(date2))
    """
    return DateComparison(date_time=date_time, operation="equal", ignore_time=True)


def close_to_datetime(date_time, seconds=5):
    """ Проверить даты на соответствие с погрешностью до <seconds> секунд
    :param date_time: дата в формате datetime, которую нужно сравнить с эталонной
    :param seconds: допустимая погрешность в сравнении дат, в секундах (по умолчанию 5)

    Пример использования:
    assert_that(date1, is_equal_to_date_ignoring_seconds(date2)) - сравнит даты с погрешностью до 5 секунд
                                                                   (по умолчанию, включительно)
    assert_that(date1, is_equal_to_date_ignoring_seconds(date2, seconds=2)) - сравнит даты с погрешностью до 2 секунд
    """
    return DateComparison(date_time=date_time, error_seconds=seconds, operation="equal with error")


class IsDate(BaseMatcher):
    """ Матчер проверяет, что значение является датой в одной из 3 форматов: SDP, datetime, timestamp """

    def _matches(self, item):
        item_date = DateTimeApi(item)
        return item_date.is_date()

    def describe_to(self, description):
        description.append_text("Value is date")

    def describe_mismatch(self, item, mismatch_description):
        mismatch_description.append_text(f"Value <{item}> does not match date format")


def is_date():
    """ Проверить, является ли значение датой в одном из 3 форматов
    Пример использования:
    assert_that(value, is_date())
    """
    return IsDate()


class IsToday(BaseMatcher):
    """ Матчер проверяет, является ли дата сегодняшней (без учета времени) """

    def __init__(self, **kwargs):
        """
        :param expected_message: текст ожидаемого результата
        :param kwargs: сюда можно передать временной сдвиг
                       Доступные значения: weeks, days, hours, minutes, seconds
        """
        self.time_shift = kwargs
        self.expected_message = self._generate_expected_message()
        self.error = None

    def _generate_expected_message(self):
        """ Метод генерирует первую часть сообщения об ошибке (там, где ожидаемая часть)
        """
        expected_message = "today"
        message_addition = ""
        for i, k in enumerate(self.time_shift):
            if k in ["weeks", "days", "hours"]:
                if i > 0:
                    message_addition += " and "
                message_addition += f"{self.time_shift[k]} {k}"

        if message_addition:
            expected_message += f" with time shift of {message_addition}"

        if len(self.time_shift) == 1:
            if self.time_shift.get("days") == 1 or self.time_shift.get("hours") == 24:
                expected_message = "tomorrow"
            elif self.time_shift.get("days") == -1 or self.time_shift.get("hours") == -24:
                expected_message = "yesterday"

        return expected_message

    def _matches(self, item):
        item_date = DateTimeApi(item)
        if not item_date.is_date():
            self.error = True
            return False

        expected_date = DateTimeApi().today().customize_date(**self.time_shift).to_date_without_time()
        return item_date.to_date_without_time() == expected_date

    def describe_to(self, description):
        description.append_text(f"Datetime is {self.expected_message}")

    def describe_mismatch(self, item, mismatch_description):
        if self.error:
            mismatch_description.append_text(f"Value <{item}> does not match date format")
        else:
            item = DateTimeApi(item)
            mismatch_description.append_text(f"Actual date: <{item.to_date_without_time()}>")


def is_today():
    """ Проверить, является ли дата текущей (без учета времени)
    Пример использования:
    assert_that(date, is_today())
    """
    return IsToday()


def is_tomorrow():
    """ Проверить, является ли дата завтрашней (без учета времени)

    Пример использования:
    assert_that(date, is_tomorrow())
    """
    return IsToday(hours=24)


def is_yesterday():
    """ Проверить, является ли дата вчерашней (без учета времени)

    Пример использования:
    assert_that(date, is_yesterday())
    """
    return IsToday(hours=-24)


def is_today_with_shift(weeks=None, days=None, hours=None):
    """ Проверить, является ли дата текущей со сдвигом
    Можно указать только недели, дни и/или часы (в том числе отрицательные значения)
    Время здесь не учитывается
    Если не передать сдвиг, то действует аналогично is_today() (тогда рекомендуется использовать is_today())

    Пример использования:
    assert_that(date, is_today_with_shift(weeks=-1)) # проверка, что date на 1 неделю раньше текущего дня
    """
    params = {k: v for k, v in locals().items() if k in ["weeks", "days", "hours"] and v is not None}
    return IsToday(**params)
