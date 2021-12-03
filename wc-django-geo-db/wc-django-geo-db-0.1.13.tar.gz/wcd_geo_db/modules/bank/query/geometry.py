from typing import Optional, Sequence, Tuple, TypeVar

from django.contrib.gis.geos.point import Point
from django.contrib.gis.measure import Distance
from django.db.models import Q

from .base import QuerySet


__all__ = 'WithGeometryQuerySet', 'Area',

QT = TypeVar('QT', bound='WithGeometryQuerySet')
Area = Tuple[Point, Distance]


def in_areas_Q(
    areas: Sequence[Area],
    field_name: str = 'location'
):
    q = Q()

    for point, distance in areas:
        q |= Q(**{f'{field_name}__distance__lte': (point, distance)})

    return q


class WithGeometryQuerySet(QuerySet):
    def in_location_areas(self, areas: Sequence[Area]):
        return self.filter(in_areas_Q(
            areas, field_name='geometry__location'
        ))

    def general_filter(
        self: QT,
        location_areas: Optional[Sequence[Area]] = None,
        **kw
    ) -> QT:
        q = super().general_filter(**kw)

        if location_areas is not None:
            return q.in_location_areas(areas=location_areas)

        return q
