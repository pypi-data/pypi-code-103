from abc import ABCMeta, abstractmethod
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, cast

from inflection import singularize
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Query, Session, aliased
from sqlalchemy.sql import Join
from sqlalchemy.sql.elements import BinaryExpression

from .typing import ResponseType

__all__ = [
    'AbstractView',
    'AbstractRESTView',
    'AbstractJoinableView',
    'AbstractIdFilterableView',
]


class AbstractView(metaclass=ABCMeta):
    """
    Abstract root view.
    """
    @abstractmethod
    def _add_error(self, *args, **kwargs) -> None:
        """Adding some errors during request handling."""

    @abstractmethod
    def _render_error(self, *args, **kwargs) -> ResponseType:
        """Rendering errors (return response with errors)."""

    @abstractmethod
    def _render(self, *args, **kwargs) -> ResponseType:
        """Rendering valid answer."""

    @property
    @abstractmethod
    def _get_params(self) -> Any:
        """Getting GET params from request."""

    @abstractmethod
    def _get_params_getall(self, param: str) -> Sequence[str]:
        """Getting multiple-defined GET param values."""


_HTTP_OPTIONS = 'get', 'head', 'post', 'put', 'delete'


class AbstractRESTView(AbstractView):
    """
    Abstract REST view.
    """
    inflection_enabled: bool = True

    @property
    @abstractmethod
    def _db_session(self) -> Session: ...

    @property
    @abstractmethod
    def _db_cls(self) -> DeclarativeMeta: ...

    @property
    @abstractmethod
    def _current_route_parts(self) -> Sequence[str]: ...

    @property
    def _item_label(self) -> str:
        return self._current_route_parts[-2]

    @property
    def _collection_label(self) -> str:
        return self._current_route_parts[-1]

    @property
    def _item_from_collection_label(self) -> str:
        if not self.__class__.inflection_enabled:
            return self._collection_label
        return singularize(self._collection_label)

    def options(self) -> ResponseType:
        """
        Формирование ответа для options запроса единицы

        :return:
        """
        return self._render(
            ', '.join((
                option.upper()
                for option in _HTTP_OPTIONS
                if hasattr(self, option)
            )),
        )

    def collection_options(self) -> ResponseType:
        """
        Формирование ответа для options запроса коллекции

        :return:
        """
        return self._render(
            ', '.join((
                option.upper()
                for option in _HTTP_OPTIONS
                if hasattr(self, f'collection_{option}')
            )),
        )


class AbstractIdFilterableView(AbstractRESTView):

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

    def __init__(
        self,
        *args,  # pylint: disable=unused-argument  # noqa
        **kwargs,  # pylint: disable=unused-argument  # noqa
    ) -> None:
        super().__init__()
        self._db_filters: List[BinaryExpression] = []

    def v_only_ids(
        self,
        *args,  # pylint: disable=unused-argument  # noqa
        **kwargs,  # pylint: disable=unused-argument  # noqa
    ) -> None:
        """
        Валидатор для добавления фильтрации только по указанным в query
        параметрах идентификаторам.
        """
        ids = self._get_params_getall('ids') or self._get_params_getall('ids[]')
        if not ids:
            return

        self._db_filters.append(self._db_cls.id.in_(ids))


class AbstractJoinableView(AbstractIdFilterableView):

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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._aliased_db_cls = aliased(self._db_cls)
        self._db_joins: Dict[str, str] = {}
        self._db_query: Query = self._db_session.query(self._db_cls)

    def _add_joins_to_query(
        self,
        joins_to_load: Tuple[str, ...],
        clauses: Optional[Mapping[str, Join]] = None,
    ) -> Optional[Query]:
        if not self._db_joins:
            return None

        if clauses is None:
            clauses: Mapping[  # type: ignore[no-redef]
                str, Join
            ] = MappingProxyType({})

        relationships = inspect(self._db_cls).relationships

        join_entities = {}

        for model_name, join_type in self._db_joins.items():
            relationship_cls = relationships[model_name].mapper.class_

            if relationship_cls is self._db_cls:
                # отношение указывает на класс модели, необходим алиас
                relationship_cls = self._aliased_db_cls

            self._db_query = getattr(self._db_query, join_type)(
                relationship_cls,
                cast(Mapping[str, Join], clauses).get(
                    model_name, relationships[model_name].class_attribute,
                ),
            )

            if model_name in joins_to_load:
                join_entities[model_name] = relationship_cls

        if not join_entities:
            return self._db_query

        # добавление entities в query в строгой последовательности согласно
        # листа joins_to_load
        for _, entity_cls in sorted(
            join_entities.items(), key=lambda x: joins_to_load.index(x[0]),
        ):
            self._db_query = self._db_query.add_entity(entity_cls)

        return self._db_query
