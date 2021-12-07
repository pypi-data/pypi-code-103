import re
from datetime import datetime, timedelta


class DateTimeApi:
    """ Класс с набором API для работы с датами
    Особенность использования: если не указать, в каком формате получить дату
    (метод to_sdp_format(), to_datetime_format(), to_timestamp_format()), то она будет в формате объекта DateTimeApi и
    в таком виде ее нельзя сравнивать с другими датами, которые в вышеперечисленных форматах. Поэтому нужно каждый раз
    указывать, в каком формате получить дату.
    Например: DateTimeApi().today().to_midnight().to_datetime_format() - сегодня, полночь, в datetime-формате

    Примеры использования:

    1) Получить дату в различных форматах
    from common.date_time_helper import DateTimeApi
    date_time = DateTimeApi()
    today = date_time.today().to_sdp_format() # сегодня в SDP-формате
    tomorrow = date_time.tomorrow().to_datetime_format() # завтра в формате питоновского datetime
    yesterday = date_time.yesterday().to_timestamp_format() # вчера в формате timestamp
    after_365_days = date_time.today().customize_date(days=365).to_date_without_time() # дата на 365 дней позже текущей
                                                                                       в формате datetime без времени
                                                                                       (только дата)
    today_midnight = date_time.today().change_time().to_datetime_format() # полночь сегодня в datetime формате
    today_noon = date_time.today().change_time(time="12:00:00").to_sdp_format() # полдень сегодня в SDP формате

    2) Проверить значение на соответствие одному из форматов даты (или конкретному)
    from common.date_time_helper import DateTimeApi
    value = "03/03/2019 08:58:59"
    date_time = DateTimeApi(value)
    date_time.is_date() # True, так как значение является датой в SDP-формате
    date_time.is_datetime_date() # False, так как значение НЕ является объектом даты datetime

    3) Перевести дату в один из трех доступных форматов: datetime, timestamp, sdp
    from common.date_time_helper import DateTimeApi
    value = "03/03/2019 08:58:59"
    date_time = DateTimeApi(value)
    date_time.to_datetime_format() # Объект datetime
    date_time.to_timestamp_format() # timestamp-формат

    4) Перевести дату в формат datetime без времени
    from common.date_time_helper import DateTimeApi
    date_without_time = DateTimeApi().today().to_date_without_time() # Объект datetime без времени

    5) Сгенерировать дату по входным параметрам (по умолчанию будет время 00:00:00)
    from common.date_time_helper import DateTimeApi
    date1 = DateTimeApi().exact_date(25, 3, 2020) # дата в datetime-формате 25 марта 2020 года 00:00:00
    date2 = DateTimeApi().exact_date(5, 2, 2019 13, 59, 59) # 5 февраля 2019 года 13:59:59
    date3 = DateTimeApi().exact_date(day=1, month=1, year=2020) # 1 января 2020 года 00:00:00

    6) Изменить дату (дни, месяц, год, часы, минуты, секунды)
    from common.date_time_helper import DateTimeApi
    date = DateTimeApi().today().change_date(hour=13, minute=40).to_datetime_format() # сегодня сейчас с изменением
                                                                                      # часов на 13 и минут на 40
                                                                                      # в datetime формате
    """
    def __init__(self, date_time=None):
        self.date_time = date_time
        self.date_format_error = f"Значение <{self.date_time}> не является датой ни в одном из доступных форматов. " \
                                 f"Доступные форматы: datetime, timestamp, sdp-формат, cms-формат"
        self.sdp_format = "%m/%d/%Y %H:%M:%S"
        self.sdp_format_regexp = r"(0[1-9]|1[012])" \
                                 r"/(0\d|1\d|2\d|3[01])" \
                                 r"/((19[789]|2\d\d)\d)" \
                                 r"\s([01]\d|2[0-3])" \
                                 r":([0-5]\d)" \
                                 r":([0-5]\d)"

        self.cms_format = "%Y-%m-%dT%H:%M:%S"
        self.cms_format_regexp = r"((19[789]|2\d\d)\d)"\
                          r"-(0[1-9]|1[012])"\
                          r"-(0\d|1\d|2\d|3[01])"\
                          r"T([01]\d|2[0-3])"\
                          r":([0-5]\d):([0-5]\d)"

        # Здесь можно задавать нужные для использования форматы даты
        # Тогда они будут автоматически конвертироваться в требуемый формат
        self.custom_date_formats = [{"format": "%d.%m.%Y %H:%M:%S", "regexp": r"(0\d|1\d|2\d|3[01])"
                                                                              r".(0[1-9]|1[012])"
                                                                              r".((19[789]|2\d\d)\d)"
                                                                              r"\s([01]\d|2[0-3])"
                                                                              r":([0-5]\d)"
                                                                              r":([0-5]\d)"},
                                    {"format": "%Y-%m-%d %H:%M:%S", "regexp": r"((19[789]|2\d\d)\d)"
                                                                              r"-(0[1-9]|1[012])"
                                                                              r"-(0\d|1\d|2\d|3[01])"
                                                                              r"\s([01]\d|2[0-3])"
                                                                              r":([0-5]\d)"
                                                                              r":([0-5]\d)"},
                                    ]

        self.custom_date_format = None

    def is_date_in_one_of_custom_formats(self):
        """ Проверить, является ли значение датой в одном из заданных пользовательских форматах """
        for i in self.custom_date_formats:
            value_is_date = \
                re.fullmatch(i["regexp"], f"{self.date_time}") if self.date_time is not None else None
            if value_is_date:
                self.custom_date_format = i["format"]
                return True
        return False

    def is_sdp_date(self):
        """ Функция определяет, является ли значение датой в SDP-формате """
        value_is_sdp_date = \
            re.fullmatch(self.sdp_format_regexp, f"{self.date_time}") if self.date_time is not None else None
        return True if value_is_sdp_date else False

    def is_cms_date(self):
        """ Функция определяет, является ли значение датой в CMS-формате """
        if self.date_time is not None:
            value_is_cms_date = re.match(self.cms_format_regexp, f"{self.date_time}")
            if value_is_cms_date:
                return True
        return False

    def is_timestamp_date(self):
        """ Функция определяет, является ли значение датой в timestamp-формате
        По сути, даже значение 0 или 1 может являться датой в timestamp-формате
        Если не удалось перевести дату в datetime формат - значит дата не является timestamp
        Если TypeError при попытке выполнить int() - значит дата не является timestamp
        """
        try:
            datetime.fromtimestamp(int(self.date_time))
            return True
        except (AttributeError, ValueError, TypeError):
            return False

    def is_datetime_date(self):
        return True if isinstance(self.date_time, datetime) else False

    def to_datetime_format(self):
        """ Функция переводит дату в datetime-формат """
        if self.is_datetime_date():
            return self.date_time
        elif self.is_sdp_date():
            return datetime.strptime(self.date_time, self.sdp_format)
        elif self.is_cms_date():
            return self.__fromisoformat()
        elif self.is_timestamp_date():
            return datetime.fromtimestamp(int(self.date_time))
        elif self.is_date_in_one_of_custom_formats():
            return datetime.strptime(self.date_time, self.custom_date_format)
        else:
            raise ValueError(self.date_format_error)

    def to_sdp_format(self):
        """ Функция переводит дату в SDP-формат
        Возвращает строку с датой в SDP-формате
        """
        if self.is_sdp_date():
            return self.date_time
        elif self.is_datetime_date():
            return str(self.date_time.strftime(self.sdp_format))
        elif self.is_timestamp_date():
            date_time = datetime.fromtimestamp(int(self.date_time))
            return str(date_time.strftime("%m/%d/%Y %H:%M:%S"))
        elif self.is_date_in_one_of_custom_formats():
            self.to_datetime_format()
            return str(self.date_time.strftime(self.sdp_format))
        else:
            raise ValueError(self.date_format_error)

    def to_timestamp_format(self):
        """ Функция переводит дату в timestamp-формат без миллисекунд (число) """
        if self.is_timestamp_date():
            return self.date_time
        else:
            return self.to_datetime_format().timestamp()

    def is_date(self):
        """ Функция определяет, является ли переданное значение датой """
        return True if self.is_sdp_date() or self.is_datetime_date() or self.is_timestamp_date() or self.is_cms_date() \
                       or self.is_date_in_one_of_custom_formats() else False

    def to_date_without_time(self):
        """ Функция переводит дату в формат даты без времени """
        date_time = self.to_datetime_format()
        return date_time.date()

    def today(self):
        """ Функция возвращает текущую дату и время """
        self.date_time = datetime.today()
        return self

    def tomorrow(self):
        """ Функция возвращает дату на сутки вперед """
        self.date_time = datetime.today() + timedelta(hours=24)
        return self

    def yesterday(self):
        """ Функция возвращает дату на сутки назад """
        self.date_time = datetime.today() + timedelta(hours=-24)
        return self

    def customize_date(self, weeks=None, days=None, hours=None, minutes=None, seconds=None):
        """ Функция возвращает дату, отличающуюся от исходной на переданное значение
        Можно указать также отрицательные значения, например weeks=-1 - дата будет на неделю раньше
        """
        self.date_time += timedelta(**{k: v for k, v in locals().items() if k != "self" and v is not None})
        return self

    def exact_date(self, day, month, year, hour=None, minute=None, second=None):
        """ Функция позволяет сгенерировать нужную дату по входным параметрам
        Месяц, день и год являются обязательными
        Если не указать время - оно будет 00:00:00
        """
        self.date_time = datetime(**{k: v for k, v in locals().items() if k != "self" and v is not None})
        return self

    def change_date(self, month=None, day=None, year=None, hour=None, minute=None, second=None):
        """ Функция выставляет заданное время текущему datetime """
        self.date_time = self.to_datetime_format()
        self.date_time = self.date_time.replace(**{k: v for k, v in locals().items() if k != "self" and v is not None})
        return self

    def to_midnight(self):
        """ Функция проставляет дате время полночь, то есть 00:00:00 """
        self.change_date(hour=0, minute=0, second=0)
        return self

    def to_custom_string(self, date_format):
        """ Функция возвращает дату в str в заданном формате
        :param date_format: формат даты (задается как в datetime)
        Пример: "%Y-%m-%d %H:%M:%S" - (год-месяц-день часы:минуты:секунды)
        """
        return self.to_datetime_format().strftime(date_format)
    
    def __fromisoformat(self):
        """Функция преобразования из ISO формат в datetime
        P.S. для обратной совместимости с 3.6 пришлось писать свою версию datetime.fromisoformat()"""
        try:
            return datetime.strptime(self.date_time, '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError as e:
            return datetime.strptime(self.date_time, '%Y-%m-%dT%H:%M:%S')
        
# ------------------ Экземпляры класса DateTimeApi для упрощённого использования --------------

today = DateTimeApi().today()
""" Получить сегодняшнюю дату в формате DateTimeApi-объекта.

    Пример использования:
    
    from common.datetime_helper import today
    
    today_as_sdp_date = today.to_sdp_format() 
    
    # вывести сегодняшнюю дату в SDP-формате
"""

yesterday = DateTimeApi().yesterday()
""" Получить вчерашнюю дату в формате DateTimeApi-объекта

    Пример использования:
    
    from common.datetime_helper import yesterday
    
    yesterday_as_sdp_date = yesterday.to_sdp_format() 
    
    # вывести вчерашнюю дату в SDP-формате
"""

tomorrow = DateTimeApi().tomorrow()
""" Получить завтрашнюю дату в формате DateTimeApi-объекта

    Пример использования:
    
    from common.datetime_helper import tomorrow
    
    tomorrow_as_sdp_date = tomorrow.to_sdp_format() 
    
    # вывести завтрашнюю дату в SDP-формате
"""
