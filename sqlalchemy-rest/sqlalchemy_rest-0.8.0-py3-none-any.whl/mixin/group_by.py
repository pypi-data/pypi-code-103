from abc import ABCMeta, abstractmethod
from functools import partial
from operator import contains
from types import MappingProxyType
from typing import FrozenSet, MutableMapping, Optional, Sequence, \
    Tuple

from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta

from ..container import GroupBy, GroupByRelationship

__all__ = [
    'AbstractGroupByViewMixin',
]


class AbstractGroupByViewMixin(metaclass=ABCMeta):
    """
    Abstract view for grouping
    """
    @abstractmethod
    def _get_params_getall(self, param: str) -> Sequence[str]: ...

    def _get_group_by_params(self, model_fields: FrozenSet[str]) -> Optional[
        Tuple[str, ...]
    ]:
        """
        Получение параметров group_by.

        :param model_fields: Список доступных полей основной модели.
        :return:
        """
        group_by_params = self._get_params_getall('group_by')
        if not group_by_params:
            return None

        group_by_params = tuple(
            filter(
                partial(contains, model_fields),
                group_by_params,
            ),
        )

        if not group_by_params:
            return None

        return group_by_params

    def _handle_group_by_params(
        self,
        db_cls: DeclarativeMeta,
        db_joins: MutableMapping[str, str],
    ) -> GroupBy:
        mapper = inspect(db_cls)

        group_by_params = self._get_group_by_params(
            frozenset(mapper.columns.keys())
        )
        if not group_by_params:
            return GroupBy()

        relationships = mapper.relationships
        relationships_map = {
            # fixme: получать ключ более гибко
            f'{key}_id': key for key in relationships.keys()
        }

        # при группировке невозможна стыковка никаких моделей, кроме тех,
        # поля которых участвуют в группировке
        allowed_relationships = frozenset(
            relationship
            for column_key, relationship in relationships_map.items()
            if column_key in group_by_params
        )
        for key in tuple(db_joins):
            if key not in allowed_relationships:
                del db_joins[key]

        return GroupBy(
            group_by_params,
            tuple(
                getattr(db_cls, c).label(c) for c in group_by_params
            ),
            MappingProxyType({
                column_key: GroupByRelationship(
                    relationship_key,
                    relationships[relationship_key].mapper.class_,
                )
                for column_key, relationship_key in relationships_map.items()
                if column_key in group_by_params
            }),
        )
