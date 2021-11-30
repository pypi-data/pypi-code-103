from typing import Any, Callable, MutableMapping, Optional, Sequence
from urllib.parse import unquote

import ujson

__all__ = [
    'param_setter_factory',
    'json_param_normalizer_factory',
]


def param_setter_factory(
    fillable_dict: MutableMapping[str, Any],
    prepare_value: Optional[Callable[[Any], Any]] = None,
) -> Callable[[str, Any], None]:
    """
    Фабрика для настройки функции аггрегирования параметров определенного
    типа в объект.

    :param fillable_dict: объект, в который аггрегируются параметры
    :param prepare_value: функция для подготовки/валидации значения
    :return:
    """

    def fill(column_name: str, value: Any) -> None:
        """
        Установка параметра согласно его наименованию. Для
        сложных аттрибутов (через точку) происходит группировка по
        префиксу до точки.

        :param column_name: наименование колонки (из GET-параметра)
        :param value: значение колонки
        :return:
        """
        if callable(prepare_value):
            value = prepare_value(value)

        splited_column_name = column_name.split('.', 1)

        if len(splited_column_name) == 1:
            # простая колонка
            fillable_dict[column_name] = value
            return

        # сложная колонка с префиксом. данный фильтр группируется по
        # префиксу
        if splited_column_name[0] not in fillable_dict:
            fillable_dict[splited_column_name[0]] = {}

        fillable_dict[splited_column_name[0]][splited_column_name[1]] = value

    return fill


def json_param_normalizer_factory(
    column_names: Sequence[str],
) -> Callable[[Any, Callable[[str, Any], None]], bool]:
    """
    Фабрика для нормализации параметра, который может быть строкой или
    json url-encoded массивом

    :param column_names: имена колонок, переданные в запросе
    :return:
    """
    def value_transformer(
        value: Any,
        set_value: Callable[[str, Any], None],
    ) -> bool:
        # парсинг search параметра
        try:
            search_list = ujson.loads(unquote(value))
            if not isinstance(search_list, list):
                raise ValueError()

        except (TypeError, ValueError):
            for column_name in column_names:
                set_value(column_name, value)

            return False

        for index, column_name in enumerate(column_names):
            try:
                value = search_list[index]

            except IndexError:
                continue

            if not value:
                continue

            set_value(column_name, value)

        return True

    return value_transformer
