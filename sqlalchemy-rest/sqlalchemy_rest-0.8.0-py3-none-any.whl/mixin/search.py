from abc import ABCMeta, abstractmethod
from typing import Any, Dict, MutableMapping, Optional, Union, cast as type_cast
from urllib.parse import unquote

from sqlalchemy import Column, String, cast, func, inspect, not_
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql import ClauseElement

from .params import json_param_normalizer_factory, \
    param_setter_factory
from ..container import Search, SearchParams

__all__ = [
    'add_search_filter',
    'AbstractSearchViewMixin',
]


# карта выражений для LIKE по типу фильтра
_SEARCH_TYPE_MAP = {
    0: '%{}%',
    1: '{}',
    2: '{}%',
    3: '%{}',
}


def add_search_filter(
    col: Union[Column, InstrumentedAttribute],
    val: Any,
    stype: Optional[int] = None,
) -> Optional[ClauseElement]:
    """
    Добавление фильтра поиска.

    :param col: экземпляр колонки модели
    :param val: значение параметра поиска
    :param stype: тип фильтра - целое число
    :return:
    """
    if not stype:
        stype = 0

    not_expr, type_id = divmod(stype, 10)

    if type_id != 1:
        # параметр search_type не объявляет строгий поиск
        search_expr = func.lower(
            cast(col, String),
        ).like(
            _SEARCH_TYPE_MAP.get(type_id, '%{}%').format(
                str(val).lower(),
            ),
        )

    elif col.type.python_type is str:
        # search_type объявил строгий поиск и тип колонки sql - строка
        search_expr = func.lower(col) == val.lower()

    else:
        # search_type объявил строгий поиск и тип колонки sql не
        # строка (попытка преобразования введенного значения val в
        # search)
        try:
            search_expr = col == col.type.python_type(val)

        except (TypeError, ValueError):
            return None

    if not_expr:
        search_expr = not_(search_expr)

    return search_expr


class AbstractSearchViewMixin(metaclass=ABCMeta):
    """
    Mixin для поиска
    """

    @property
    @abstractmethod
    def _get_params(self) -> Any: ...

    def _get_search_params(self) -> SearchParams:
        """
        Получение GET параметров, относящихся к поиску

        :return:
        """
        get_params = self._get_params

        if 'search' not in get_params or 'column_names' not in get_params:
            # не указаны параметры поиска
            return SearchParams()

        # просмотр параметра поиска
        search_param = get_params['search'].strip()
        if not search_param:
            return SearchParams()

        column_names = tuple(
            map(
                lambda name: name.strip().lower(),
                unquote(get_params['column_names']).split(','),
            ),
        )
        json_param_normalizer = json_param_normalizer_factory(column_names)

        # формирование объекта поиска
        search: Dict[str, Union[str, Dict[str, str]]] = {}
        search_param_setter = param_setter_factory(search)
        and_joint = json_param_normalizer(search_param, search_param_setter)

        # разбираем типы фильтров, отправленные в запросе
        search_type_param = get_params.get('search_type')
        search_type: Dict[str, Union[int, Dict[str, int]]] = {}
        if search_type_param:
            # 0 - contains
            # 1 - matches
            # 2 - startswith
            # 3 - endswith
            # 10 - not contains
            # 11 - not matches
            # 12 - not startswith
            # 13 - not endswith

            def search_type_preparer(val):
                try:
                    return abs(int(val))
                except (ValueError, TypeError):
                    return 0

            search_type_param_setter = param_setter_factory(
                search_type, prepare_value=search_type_preparer,
            )
            json_param_normalizer(
                search_type_param.strip(),
                search_type_param_setter,
            )

        return SearchParams(
            search=search,
            and_joint=and_joint,
            search_type=search_type,
        )

    def _handle_search_params(
        self,
        db_cls: DeclarativeMeta,
        db_joins: MutableMapping[str, str],
        aliased_db_cls: Optional[AliasedClass] = None,
    ) -> Search:
        """
        Обработка поиска по коллекции

        :param db_cls: Объект модели Sqlalchemy.
        :param db_joins: Словарь стыковки моделей по типу (inner или outer).
        :param aliased_db_cls: Алиса объекта модели (требуется если отношение
        для модели является self-referenced).
        :return:
        """
        mapper = inspect(db_cls)
        search_params = self._get_search_params()

        if not search_params.search:
            return Search(search_params)

        search_filters = []

        # формируем ключи отношений, согласно описанию orm
        relationship_keys = mapper.relationships.keys()

        search_type = search_params.search_type

        for column_name, search_value in search_params.search.items():

            if not isinstance(search_value, dict):
                # простая колонка без префикса

                if column_name not in mapper.columns.keys():
                    # такой колонки нет для текущей модели
                    continue

                column = getattr(db_cls, column_name)
                search_expr = add_search_filter(
                    column,
                    search_value,
                    type_cast(Dict[str, int], search_type).get(column_name),
                )
                search_filters.append(search_expr)
                continue

            if column_name not in relationship_keys:
                # такого отношения нет для текущей модели
                continue

            # innerjoin если по И, outerjoin если по ИЛИ
            db_joins[column_name] = \
                'join' if search_params.and_joint else 'outerjoin'

            for rel_column_name, rel_value in search_value.items():
                rel_cls = mapper.relationships[column_name].mapper.class_
                if not hasattr(rel_cls, rel_column_name):
                    continue

                if rel_cls is db_cls:
                    # отношение указывает на класс текущей модели, необходим
                    # алиас
                    rel_cls = aliased_db_cls

                # добавление фильтров по связанным моделям
                search_expr = add_search_filter(
                    getattr(rel_cls, rel_column_name),
                    rel_value,
                    type_cast(
                        Dict[str, int],
                        search_type.get(column_name) or {},
                    ).get(rel_column_name),
                )
                search_filters.append(search_expr)

        return Search(
            search_params,
            tuple(search_filters),
        )
