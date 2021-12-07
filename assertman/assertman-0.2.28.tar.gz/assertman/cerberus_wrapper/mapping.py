# -*- coding: utf-8 -*-


# ------  Общие матчеры (Object)  ------------------------------------------------------

def equal_to(obj):
    """ Matches if object is equal to a given object """
    schema = {"equal_to": obj}
    # по-умолчанию cerberus схема не допускает наличие None значений. При проверки на equal_to(None), отключаем
    # это ограничение, только для конкретного поля
    if obj is None:
        schema.update({"nullable": True})
    return schema


def has_length(match):
    """ Matches if ``len(item)`` satisfies a given matcher
    * матчер проверяет длинну любого sequence-типа данных: list, str, dict, tuple и кастомнный тип данных с
    переопределенным методом `__len__`
    """
    # TODO (Кузнецов М.): Дописать проверкау то что items должен быть числом или матчером

    # В случае, если используется простая проверка длинны списка (без вложенных матчеров сравнения больше или меньше)
    if isinstance(match, int):
        return {'length': match}

    # В случае, если используется проверка длинны списка с вложенными матчерами типа 'greater_than' и 'less_than'.
    # Не стал тут реализовывать обработку  матчеров 'greater_than_or_equal_to' и 'less_than_or_equal_to',
    # так как при проверке длинны списков они всегда могут быть заменены
    # на более лаконичные 'greater_than' и 'less_than')
    # Еще одна деталь, в том что 'minlength' / 'maxlength', больше сответствуют  'greater_than_or_equal_to' /
    # 'less_than_or_equal_to', чем 'greater_than' / 'less_than'.  Поэтому приходится прибавлять / удалять еденницу
    elif isinstance(match, dict):
        if match.get('greater_than'):
            return {'minlength': match.get('greater_than') + 1}
        elif match.get('less_than'):
            return {'maxlength': match.get('less_than') - 1}
        elif match.get('greater_than_or_equal_to'):
            return {'minlength': match.get('greater_than_or_equal_to')}
        elif match.get('less_than_or_equal_to'):
            return {'maxlength': match.get('less_than_or_equal_to')}
        else:
            raise Exception(f"Нельзя использовать матчер `{match}` внутри матчера `has_length`")
    else:
        raise Exception(f"Для `has_item` получен матчер, для которого не задано "
                        f"правило преобразования в схему: {type(match)}")


def is_instance_of(atype):
    """ Matches if object is an instance of, or inherits from, a given type """
    value = atype.__name__
    if value == 'str':
        value = "string"
    elif value == 'int':
        value = "integer"
    elif value == 'bool':
        value = "boolean"

    return {'type': value}


def empty():
    raise NotImplementedError


def none():
    """ Matches if object is `None` """
    return equal_to(None)


def not_none():
    """ Matches if object is not `None` """
    return not_(None)


# ------  Numbers  ------------------------------------------------------

def greater_than(value):
    """ Matches if object is greater than a given value """
    _check_isinstance(value, (int, float))
    return {'greater_than': value}


def greater_than_or_equal_to(value):
    """ Matches if object is greater than or equal to a given value """
    _check_isinstance(value, (int, float))
    return {'greater_than_or_equal_to': value}


def less_than(value):
    """ Matches if object is less_than a given value """
    _check_isinstance(value, (int, float))
    return {'less_than': value}


def less_than_or_equal_to(value):
    """ Matches if object is less_than_or_equal_to a given value """
    _check_isinstance(value, (int, float))
    return {'less_than_or_equal_to': value}


def close_to(value, delta):
    """ Matches if object is a number close to a given value, within a given delta """
    _check_isinstance(value, (int, float))
    _check_isinstance(delta, (int, float))
    return {'close_to': (value, delta), 'type': 'integer'}


# ------  Text  ------------------------------------------------------

def starts_with(substring):
    """ Matches if object is a string starting with a given string """
    _check_isinstance(substring, str)
    return {"starts_with": substring}


def contains_string(substring):
    """ Matches if object is a string containing a given string. """
    _check_isinstance(substring, str)
    return {"contains_string": substring}


def string_contains_in_order(substrings):
    """ Matches if object is a string containing a given list of substrings in relative order. """
    _check_isinstance(substrings, tuple)
    for i in substrings:
        _check_isinstance(i, str)
    return {"string_contains_in_order": substrings}


def ends_with(substring):
    """ Matches if object is a string ending with a given string """
    _check_isinstance(substring, str)
    return {"ends_with": substring}


def equal_to_ignoring_case(substring):
    """ Matches if object is a string equal to a given string, ignoring case differences """
    _check_isinstance(substring, str)
    return {"equal_to_ignoring_case": substring}


def matches_regexp(pattern):
    """ Matches if object is a string containing a match for a given regular expression """
    _check_isinstance(pattern, str)
    return {'regex': pattern}


# ------  Sequence  ------------------------------------------------------

def has_item(matcher):
    """ Matches if any element of sequence satisfies a given matcher """
    # TODO (Кузнецов М.): Добавить проверку  matcher
    return {'type': 'list', 'required': True, 'empty': False, "has_item": matcher}


def _not_has_item(matcher):
    """ Matches if any element of sequence NOT satisfies a given matcher """
    return {'type': 'list', 'required': True, 'empty': False, "not_has_item": matcher}


def every_item(matcher):
    """ Matches if every element of sequence satisfies a given matcher """
    # TODO (Кузнецов М.): Добавить проверку  matcher
    return {'type': 'list', 'required': True, 'empty': False, "every_item": matcher}


def has_item_at_index(index, matcher):
    """Проверить, что в списке элемент с переданным индексом удовлетворяет переданному матчеру."""
    return {'type': 'list', 'required': True, 'empty': False, "has_item_at_index": (index, matcher)}


def has_first_item(matcher):
    """Проверить, что в списке  первый элемент  удовлетворяет переданному матчеру."""
    return has_item_at_index(0, matcher)


def has_last_item(matcher):
    """Проверить, что в списке  последний элемент  удовлетворяет переданному матчеру."""
    return has_item_at_index(-1, matcher)


def has_items(matchers):
    """ Matches if any element of sequence satisfies a given matchers """
    matchers_to_list_has_item = [extract(i) for i in matchers]
    return {'type': 'list', 'required': True, 'empty': False, "has_items": [i['has_item'] for i in matchers_to_list_has_item]}

# ------  Dictionary  ------------------------------------------------------

def has_entries(*keys_valuematchers, **kv_args):
    schema = {}

    def add_to_scheme(_dict):
        for k, v in _dict.items():
            if k not in schema:
                schema.update({k: extract(v)})
            else:
                schema[k].update(extract(v))

    if keys_valuematchers:
        if len(keys_valuematchers) > 1 and not isinstance(keys_valuematchers[0], dict):
            raise ValueError('has_entries requires key-value pairs or dict with matchers')
        add_to_scheme(keys_valuematchers[0])

    add_to_scheme(kv_args)

    return {'schema': schema, 'type': 'dict'}


def has_key(key_match):
    return {'has_key': key_match}



# ------  Logical  ------------------------------------------------------

def all_of(*items):
    """ Matches if all of the given matchers evaluate to ``True`` """
    # TODO (Кузнецов М.): Дописать проверку на то, что items должен быть список матчеров
    return {'allof': items}


def any_of(*items):
    """ Matches if any of the given matchers evaluate to ``True`` """
    # TODO (Кузнецов М.): Дописать проверку то что items должен быть список матчеров
    return {'anyof': items}


# ------  Datetime  ------------------------------------------------------
def is_today():
    """ Матчер проверки, что дата является сегодняшней (без учета времени) """
    return is_today_with_shift()


def is_tomorrow():
    """ Матчер проверки, что дата является завтрашней (без учета времени) """
    return is_today_with_shift(hours=24)


def is_yesterday():
    """ Матчер проверки, что дата является вчерашней (без учета времени) """
    return is_today_with_shift(hours=-24)


def is_today_with_shift(weeks=None, days=None, hours=None, message=None):
    """ Матчер проверки, что дата является сегодняшней с заданным сдвигом """
    return {"is_today_with_shift": {"weeks": weeks, "days": days, "hours": hours, "message": message}}


def is_greater_than_datetime(value):
    """ Проверка, что дата более поздняя, чем ожидаемая (с учетом времени) """
    return {"is_greater_than_datetime": value}


def is_less_than_datetime(value):
    """ Проверка, что дата более ранняя, чем ожидаемая (с учетом времени) """
    return {"is_less_than_datetime": value}


def is_equal_to_datetime(value):
    """ Проверка, что дата соответствует ожидаемой с учетом времени """
    return {"is_equal_to_datetime": value}


def is_greater_than_date(value):
    """ Проверка, что дата более поздняя (без учета времени) """
    return {"is_greater_than_date": value}


def is_less_than_date(value):
    """ Проверка, что дата более ранняя (без учета времени) """
    return {"is_less_than_date": value}


def is_equal_to_date(value):
    """ Проверка, что дата соответствует ожидаемой (без учета времени) """
    return {"is_equal_to_date": value}


def is_equal_to_date_ignoring_seconds(value, seconds=5):
    """ Проверка, что дата соответствует ожидаемой с учетом допустимой погрешности с 5 секунд (по умолчанию)
    В seconds можно задать допустимую погрешность
    """
    return {"is_equal_to_date_ignoring_seconds": {"value": value, "seconds": seconds}}


# ----------------- Original Cerberus matchers ---------------------------
def is_in(values):
    return {'allowed': values}


# ------  Negative  ------------------------------------------------------

class CerberusNot:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'not({self.value})'


not_ = CerberusNot


def negative(matcher):
    def matcher_type(_type):
        return _type == type(matcher).__name__

    if matcher_type('IsSequenceContaining'):
        return _not_has_item(extract(matcher.element_matcher))

    result = {}
    for k, v in extract(matcher).items():
        # Есть встроеенные в cerberus матчеры, которые почти всегда автоматически применяются
        # (типа `nullable`, 'required' и  так как они булевые, то при их инверсии достаточно сделать отрицание)
        if k in ['nullable']:
            result.update({k: not v})
        else:
            result.update({k: not_(v)})
    return result


def _check_isinstance(value, *types):
    for _type in types:
        if not isinstance(value, _type):
            raise TypeError(f"Матчер работает только с {_type}")


def extract(v, equal=True):
    """ Функция маппинга матчеров Hamcrest в матчеры Cerberus
    :param v:
    :param equal:
    :return: Cerberus marcher
    """

    def matcher_type(_type):
        return _type == type(v).__name__

    if isinstance(v, str) or isinstance(v, int) or isinstance(v, float) or isinstance(v, list) or isinstance(v, dict):
        return equal_to(v)
    elif matcher_type('IsEqual') or matcher_type('IsEqualWithDiff'):
        return equal_to(v.object) if equal == True else v.object
    elif matcher_type('StringContains'):
        return contains_string(v.substring)
    elif matcher_type('StringStartsWith'):
        return starts_with(v.substring)
    elif matcher_type('StringEndsWith'):
        return ends_with(v.substring)
    elif matcher_type('StringContainsInOrder'):
        return string_contains_in_order(v.substrings)
    elif matcher_type('IsEqualIgnoringCase'):
        return equal_to_ignoring_case(v.original_string)
    elif matcher_type('IsCloseTo'):
        return close_to(v.value, v.delta)
    elif matcher_type('HasLength'):
        return has_length(extract(v.len_matcher, equal=False))
    elif matcher_type('OrderingComparison'):
        if v.comparison_description == 'greater than':
            return greater_than(v.value)
        elif v.comparison_description == 'less than':
            return less_than(v.value)
        elif v.comparison_description == 'greater than or equal to':
            return greater_than_or_equal_to(v.value)
        elif v.comparison_description == 'less than or equal to':
            return less_than_or_equal_to(v.value)
    elif matcher_type('IsSequenceContaining'):
        return has_item(extract(v.element_matcher))
    elif matcher_type('EveryItem'):
        return every_item(extract(v.matcher))
    elif matcher_type('IsDictContainingEntries'):
        return has_entries(**{k: v for k, v in v.value_matchers})
    elif matcher_type('IsDictContaining'):
        raise Exception("Матчер `has_entry()` не портирован в Cerberus-формат. Это можно сделать, но в большинстве "
                        "случаев лучше использовать матчер `has_entries()`")
    elif matcher_type('IsDictContainingValue'):
        raise Exception("Матчер `has_value()` еще не портирован в Cerberus-формат")
    elif matcher_type('IsEmpty'):
        return has_length(0)
    elif matcher_type('AllOf'):
        return all_of(*[extract(i) for i in v.matchers])
    elif matcher_type('AnyOf'):
        return any_of(*[extract(i) for i in v.matchers])
    elif matcher_type('Is'):
        return extract(v.matcher)
    elif matcher_type('IsInstanceOf'):
        return is_instance_of(v.expected_type)
    elif matcher_type('IsNone'):
        return none()
    elif matcher_type('IsDictContainingKey'):
        return has_key(v.key_matcher.object)
    elif matcher_type('StringMatchesPattern'):
        return matches_regexp(v.pattern.pattern)
    elif matcher_type('IsNot'):
        return negative(v.matcher)
    elif matcher_type('IsToday'):
        return is_today_with_shift(**v.time_shift, message=v.expected_message)
    elif matcher_type('DateComparison'):
        if v.ignore_time is False:
            if v.operation == 'greater':
                return is_greater_than_datetime(v.actual_item)
            elif v.operation == 'less':
                return is_less_than_datetime(v.actual_item)
            elif v.operation == 'equal':
                return is_equal_to_datetime(v.actual_item)
        elif v.ignore_time is True:
            if v.operation == "greater":
                return is_greater_than_date(v.actual_item)
            elif v.operation == "less":
                return is_less_than_date(v.actual_item)
            elif v.operation == "equal":
                return is_equal_to_date(v.actual_item)
        if v.operation == "equal with error":
            return is_equal_to_date_ignoring_seconds(v.actual_item, seconds=v.error_seconds)
    elif matcher_type('HasItemAtIndex'):
        return has_item_at_index(index=v.index, matcher=extract(v.matcher))
    elif matcher_type('IsIn'):
        return is_in(v.sequence)
    elif matcher_type('IsSequenceContainingEvery'):
        return has_items(v.matcher.matchers)
    raise Exception(f"Не удалось найти правило маппинга Hamcrest-матчера '{type(v).__name__}' в Cerberus-матчер")
