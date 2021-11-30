from abc import ABCMeta, abstractmethod
from itertools import chain, repeat
from typing import Any, Mapping, MutableMapping, Optional, \
    Sequence, Tuple

from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.util import AliasedClass

from ..container import Paging, PagingParams
from ..typing import OrderByType

__all__ = [
    'AbstractPagerViewMixin',
]


class AbstractPagerViewMixin(metaclass=ABCMeta):
    """
    Mixin для постраничной навигации
    """
    @property
    @abstractmethod
    def _get_params(self) -> Any: ...

    @abstractmethod
    def _get_params_getall(self, param: str) -> Sequence[str]: ...

    DEFAULT_LIMIT: Optional[int] = None
    DEFAULT_PAGE: int = 1
    DEFAULT_SORT_BY: Optional[str] = None
    DEFAULT_ASC: str = 'false'
    MAX_LIMIT: int = 1000

    def _get_pager_params(self) -> PagingParams:
        """
        Получение GET параметров, относящихся к пэйджингу

        :return:
        """
        cls = self.__class__
        get_params = self._get_params

        try:
            page = abs(int(get_params.get('page') or 1))

        except (ValueError, TypeError):
            page = cls.DEFAULT_PAGE

        limit: Optional[int]
        try:
            limit = abs(int(get_params.get('limit')))

            if cls.MAX_LIMIT and limit > cls.MAX_LIMIT:
                limit = cls.MAX_LIMIT

        except (ValueError, TypeError):
            limit = cls.DEFAULT_LIMIT

        start = 0
        if limit:
            start = (page - 1) * limit

        sort_by_params = self._get_params_getall('sort_by')
        sort_by = sort_by_params or cls.DEFAULT_SORT_BY

        asc_params = self._get_params_getall('asc')
        desc_params = self._get_params_getall('desc')
        sort_params = self._get_params_getall('sort')

        normalized_asc_params = tuple(
            chain(
                zip(repeat('asc'), asc_params),
                zip(repeat('desc'), desc_params),
                zip(repeat('sort'), sort_params),
            ),
        )[:len(sort_by_params)]

        if len(normalized_asc_params) < len(sort_by_params):
            normalized_asc_params = normalized_asc_params + tuple(
                repeat(
                    ('asc', cls.DEFAULT_ASC),
                    len(sort_by_params) - len(normalized_asc_params),
                ),
            )

        asc = tuple(
            (direction == 'asc' and param in ('true', '1', 'yes')) or
            (direction == 'desc' and param not in ('true', '1', 'yes')) or
            (direction == 'sort' and param not in ('down', 'desc'))
            for direction, param in normalized_asc_params
        )

        return PagingParams(
            page=page, start=start, limit=limit, asc=asc, sort_by=sort_by,
        )

    def _handle_pager_params(
        self,
        db_cls: DeclarativeMeta,
        db_joins: MutableMapping[str, str],
        aliased_db_cls: Optional[AliasedClass] = None,
        order_by_map: Optional[
            Mapping[str, OrderByType]
        ] = None,
        default_order_by: Optional[
            Tuple[OrderByType, ...]
        ] = None,
        except_sort_by: Optional[Sequence[str]] = None,
    ) -> Paging:
        """
        Обработка пэйджинга (срез данных для передачи только необходимого).

        :param db_cls: Объект модели sqlalchemy.
        :param db_joins: Словарь стыковки моделей по типу (inner или outer).
        :param aliased_db_cls: Алиса объекта модели (требуется если отношение
        для модели является self-referenced).
        :param order_by_map: Карта, согласно которой нужно подставлять
        order_by параметры на основе параметров GET запроса sort_by
        :param default_order_by: Сортировка по-умолчанию.
        :param except_sort_by: Список вариантов параметра sort_by, которые
        запрещено обрабатывать.
        :return:
        """
        if except_sort_by is None:
            except_sort_by = ()

        if default_order_by is None:
            default_order_by = ()

        if order_by_map is None:
            order_by_map = {}

        mapper = inspect(db_cls)

        pager_params = self._get_pager_params()
        order_by = default_order_by
        stop: Optional[int] = None

        if pager_params.sort_by is not None:
            # управление сортировкой
            sort_by = pager_params.sort_by
            splitted_sort_by = [
                sb.split('.', 1) for sb in sort_by
            ]

            def handle_simple_column(i):
                """
                Обработка сортировки по простой колонке
                :param i: Индекс
                :return:
                """
                if sort_by[i] in order_by_map:
                    return order_by_map[sort_by[i]]

                if sort_by[i] not in mapper.columns.keys():
                    return
                return getattr(db_cls, sort_by[i])

            def handle_relation(i):
                """
                Обработка сортировки по колонке отношения
                :param i: Индекс
                :return:
                """
                if sort_by[i] in order_by_map:
                    return order_by_map[sort_by[i]]

                if splitted_sort_by[i][0] not in mapper.relationships.keys():
                    return

                if splitted_sort_by[i][0] not in db_joins:
                    # join мог быть объявлен ранее
                    db_joins[splitted_sort_by[i][0]] = 'outerjoin'

                rel_cls = mapper.relationships[
                    splitted_sort_by[i][0]
                ].mapper.class_

                if rel_cls is db_cls:
                    rel_cls = aliased_db_cls

                return getattr(rel_cls, splitted_sort_by[i][1])

            order_by = tuple(
                handle_relation(index) if len(
                    splitted_sort_by[index]
                ) == 2 else handle_simple_column(index)
                for index in range(len(sort_by))
                if sort_by not in except_sort_by
            )

            order_by_indexed = tuple(
                filter(
                    lambda x: x[1] is not None, enumerate(order_by),
                ),
            )

            if not order_by_indexed:
                order_by = default_order_by or (getattr(db_cls, 'id'), )
            else:
                order_by = tuple(
                    ob.asc() if pager_params.asc[index] else ob.desc()
                    for index, ob in order_by_indexed
                )

        if pager_params.start is not None and pager_params.limit:
            # управление величиной среза
            stop = pager_params.start + pager_params.limit

        return Paging(pager_params.start or 0, stop, order_by)
