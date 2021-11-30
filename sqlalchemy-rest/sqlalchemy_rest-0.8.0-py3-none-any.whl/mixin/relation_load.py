from abc import ABCMeta, abstractmethod
from typing import MutableMapping, Optional, Sequence, Tuple

from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta

__all__ = [
    'AbstractRelationLoadViewMixin',
]


class AbstractRelationLoadViewMixin(metaclass=ABCMeta):
    """
    Mixin для загрузки связанных моделей
    """
    @abstractmethod
    def _get_params_getall(self, param: str) -> Sequence[str]: ...

    def _get_relation_load_params(
        self,
        relation_keys: Sequence[str],
    ) -> Optional[Tuple[str, ...]]:
        """
        Получение GET параметров with
        :param relation_keys: Список строк с названиями отношений, допустимых
        для класса БД точки REST.
        :return:
        """
        with_params = self._get_params_getall('with')
        if not with_params:
            # нет заданы параметры with
            return None

        with_params = tuple(
            filter(
                lambda x: x in relation_keys, with_params,
            ),
        )

        if not with_params:
            #  параметры with не содержат ни одной валидной связи для текущей
            #  модели
            return None

        return with_params

    def _handle_relation_load_params(
        self,
        db_cls: DeclarativeMeta,
        db_joins: MutableMapping[str, str],
    ) -> Tuple[str, ...]:
        """
        Загружает дополнительно запрошенные модели из БД, связанные с
        основной моделью rest-точки для последующего их включения в ответ.

        :param db_cls: Объект модели sqlalchemy.
        :param db_joins: Словарь стыковки моделей по типу (inner или outer).
        :return:
        """
        mapper = inspect(db_cls)

        relation_load_params = self._get_relation_load_params(
            tuple(
                mapper.relationships.keys(),
            ),
        )
        if not relation_load_params:
            return ()

        for relation_load_param in relation_load_params:
            if relation_load_param not in db_joins:
                # Join мог быть определен выше
                db_joins[relation_load_param] = 'outerjoin'

        return relation_load_params
