import itertools
from abc import abstractmethod
from operator import itemgetter
from typing import Any, Dict, List, Sequence, Tuple, Union, cast

from sqlalchemy import and_, func, inspect, or_
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import BinaryExpression

from .abc import AbstractIdFilterableView, AbstractJoinableView
from .container import GroupBy, Paging, Search
from .mixin import AbstractGroupByViewMixin, AbstractPagerViewMixin, \
    AbstractRelationLoadViewMixin, \
    AbstractSearchViewMixin, add_search_filter
from .typing import ResponseType

__all__ = [
    'AbstractCollectionSimpleRESTView',
    'AbstractCollectionRelationLoadRESTView',
    'AbstractCollectionRESTView',
]


class AbstractCollectionSimpleRESTView(AbstractIdFilterableView):
    """
    Базовый view для работы с коллекциями
    """
    @abstractmethod
    def _list_item_transform(self, item: object) -> Any: ...

    def _get_all(self) -> List[object]:
        return self._db_cls.all(
            *self._db_filters,
            order_by=self._db_cls.id.asc(),
        )

    def _count_all(self) -> int:
        return self._db_cls.count(*self._db_filters)

    def collection_get(self) -> ResponseType:
        return self._render({
            self._collection_label: tuple(
                map(
                    self._list_item_transform,
                    self._get_all(),
                ),
            ),
            "meta": {
                "total": self._count_all(),
            },
        })


class AbstractCollectionRelationLoadRESTView(
    AbstractRelationLoadViewMixin,
    AbstractJoinableView,
    AbstractCollectionSimpleRESTView,
):

    @abstractmethod
    def _list_item_transform(self, item: object) -> Any: ...

    @property
    @abstractmethod
    def _db_session(self) -> Session: ...

    @property
    @abstractmethod
    def _db_cls(self) -> DeclarativeMeta: ...

    @property
    @abstractmethod
    def _current_route_parts(self) -> Sequence[str]: ...

    @abstractmethod
    def _add_error(self, *args, **kwargs) -> None: ...

    @abstractmethod
    def _render_error(self, *args, **kwargs) -> ResponseType: ...

    @property
    @abstractmethod
    def _get_params(self) -> Any: ...

    @abstractmethod
    def _get_params_getall(self, param: str) -> Sequence[str]: ...

    def collection_get(self) -> ResponseType:
        self._add_joins_to_query(
            self._handle_relation_load_params(self._db_cls, self._db_joins),
        )
        return super().collection_get()


class AbstractCollectionRESTView(
    AbstractPagerViewMixin,
    AbstractSearchViewMixin,
    AbstractRelationLoadViewMixin,
    AbstractGroupByViewMixin,
    AbstractJoinableView,
):

    @abstractmethod
    def _list_item_transform(self, item: object) -> Any: ...

    @property
    @abstractmethod
    def _db_session(self) -> Session: ...

    @property
    @abstractmethod
    def _db_cls(self) -> DeclarativeMeta: ...

    @property
    @abstractmethod
    def _current_route_parts(self) -> Sequence[str]: ...

    @abstractmethod
    def _add_error(self, *args, **kwargs) -> None: ...

    @abstractmethod
    def _render_error(self, *args, **kwargs) -> ResponseType: ...

    @property
    @abstractmethod
    def _get_params(self) -> Any: ...

    @abstractmethod
    def _get_params_getall(self, param: str) -> Sequence[str]: ...

    def _get_all(self, paging: Paging) -> List[Any]:
        query = self._db_query.filter(*self._db_filters)

        if paging.order_by:
            query = query.order_by(*paging.order_by)

        if isinstance(paging.stop, int):
            query = query.slice(paging.start, paging.stop)

        return query.all()

    def _count_all(self) -> int:
        return self._db_query.filter(*self._db_filters).count()

    def _process_group_by(
        self,
        group_by: GroupBy,
        search: Search,
        relation_load_params: Tuple[str, ...],
    ) -> Tuple[
        Dict[str, InstrumentedAttribute],
        Tuple[InstrumentedAttribute, ...],
        Tuple[str, ...],
        Tuple[str, ...],
    ]:
        joint = and_ if search.params.and_joint else or_

        cte_filters: List[BinaryExpression] = []
        cte_filters.extend(self._db_filters)
        if search.filters:
            cte_filters.append(joint(*search.filters))

        cte = self._db_query.with_entities(
            func.count(getattr(self._db_cls, 'id')).label('group_by_amount'),
            *group_by.columns,
        ).filter(
            *cte_filters
        ).group_by(
            *group_by.columns,
        ).cte()

        self._db_query = self._db_session.query(
            cte.c.group_by_amount,
            *(getattr(cte.c, column.key) for column in group_by.columns),
        )

        relationship_clauses = {
            group_by_relationship.key: getattr(cte.c, key) == getattr(
                group_by_relationship.sa_cls, 'id'
            )
            for key, group_by_relationship in group_by.relationship_map.items()
        }

        # параметры для стыковки ограничиваются только параметрами
        # группировки
        relation_load_params = tuple(
            relationship_key
            for relationship_key in relation_load_params
            if relationship_key in relationship_clauses
        )

        # формирование выборки с учетом join-ов
        self._add_joins_to_query(
            relation_load_params,
            clauses=relationship_clauses,
        )

        # разрешенная сортировка.
        order_by_map = {
            column.key: getattr(
                cte.c, column.key
            ) for column in group_by.columns
        }

        amount_column_param = 'group_by.amount', 'group_by_amount', 'amount'

        for amount_param in amount_column_param:
            order_by_map[amount_param] = cte.c.group_by_amount

        # фильтрация по количеству, если присутствует
        if search.params.and_joint or len(cte_filters) == 0:
            for amount_param in amount_column_param:
                if amount_param not in search.params.search:
                    continue

                search_expr = add_search_filter(
                    cte.c.group_by_amount,
                    search.params.search[amount_param],
                    cast(
                        Dict[str, int],
                        search.params.search_type
                    ).get(amount_param) or 0,
                )

                self._db_filters.append(search_expr)
                break

        columns = inspect(self._db_cls).columns

        return order_by_map, tuple(
            getattr(cte.c, c.key) for c in group_by.columns
        ), tuple(
            k for k in columns.keys() if k not in group_by.params
        ), relation_load_params

    def collection_get(self) -> ResponseType:
        # фильтрация
        search = self._handle_search_params(
            self._db_cls,
            self._db_joins,
            self._aliased_db_cls,
        )

        # пэйджинг
        paging = self._handle_pager_params(
            self._db_cls, self._db_joins, self._aliased_db_cls,
        )

        # обработка параметров стыковки
        relation_load_params = self._handle_relation_load_params(
            self._db_cls, self._db_joins,
        )

        # формирование выборки с учетом join-ов
        self._add_joins_to_query(relation_load_params)

        # обработка группировки
        result_shift = 1  # сдвиг получения связанных моделей
        group_by = self._handle_group_by_params(
            self._db_cls, self._db_joins,
        )

        if group_by.columns:
            result_shift = len(group_by.columns) + 1

            (
                order_by_map,
                default_order_by,
                except_sort_by,
                relation_load_params,
            ) = self._process_group_by(
                group_by,
                search,
                relation_load_params,
            )

            # пэйджинг
            paging = self._handle_pager_params(
                self._db_cls,
                self._db_joins,
                self._aliased_db_cls,
                order_by_map=order_by_map,
                default_order_by=default_order_by,
                except_sort_by=except_sort_by,
            )

        # добавление фильтрации в db_filters
        elif search.filters:
            joint = and_ if search.params.and_joint else or_
            self._db_filters.append(joint(*search.filters))

        # выборка
        db_results = self._get_all(paging)

        result: Dict[str, Union[Dict[str, Any], Sequence[Dict[str, Any]]]] = {
            'meta': {
                'total': self._count_all(),
            },
        }

        if not group_by.params and not relation_load_params:
            result[self._collection_label] = tuple(
                map(
                    self._list_item_transform,
                    db_results,
                ),
            )
            return self._render(result)

        result[self._collection_label] = tuple(
            map(
                lambda x: self._list_item_transform(x[0]),
                db_results,
            ),
        ) if not group_by.params else ()

        # добавляем в выдачу модели, которые встречаются как связанные
        # для основной модели
        for index, with_param in enumerate(relation_load_params):
            with_items: Tuple[Any, ...] = tuple(
                filter(
                    None,
                    map(itemgetter(index + result_shift), db_results),
                ),
            )
            if not with_items:
                result[with_param] = []
                continue

            result[with_param] = tuple(
                map(
                    lambda x: self._list_item_transform(x[0]),
                    itertools.groupby(with_items),
                ),
            )

        if not group_by.params:
            return self._render(result)

        # формируем данные group_by, если они есть
        group_by_data: List[Dict[str, Any]] = []
        for key, data in itertools.groupby(
            db_results,
            key=lambda x: tuple(
                x[i] for i in range(1, len(group_by.params) + 1)
            ),
        ):
            group_by_data_item = dict(zip(group_by.params, key))
            group_by_data_item['amount'] = next(data)[0]
            group_by_data.append(group_by_data_item)

        result['group_by'] = group_by_data
        return self._render(result)
