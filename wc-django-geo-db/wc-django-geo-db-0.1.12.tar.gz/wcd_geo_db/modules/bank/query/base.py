from typing import Any, Optional, Sequence, TypeVar
from django.db import models


__all__ = 'QuerySet',

QT = TypeVar('QT', bound='QuerySet')


class QuerySet(models.QuerySet):
    def optional_in(
        self: QT,
        field: str,
        items: Optional[Sequence[Any]]
    ) -> QT:
        if items is None:
            return self

        if len(items) == 1:
            return self.filter(**{field: tuple(items)[0]})

        return self.filter(**{f'{field}__in': items})

    def optional_overlap(
        self: QT,
        field: str,
        items: Optional[Sequence[Any]]
    ) -> QT:
        if items is None:
            return self

        return self.filter(**{f'{field}__overlap': items})

    def ids(self: QT):
        return self.values_list('pk', flat=True)

    def general_filter(
        self: QT,
        ids: Optional[Sequence[int]] = None,
        **kw
    ) -> QT:
        return self.optional_in('id', ids)
