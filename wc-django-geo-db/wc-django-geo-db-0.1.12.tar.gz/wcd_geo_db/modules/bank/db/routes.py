from django.db import models
from django.utils.translation import pgettext_lazy
from wcd_geo_db.modules.code_seeker.models import (
    CodesDefinableMixin, codes_mixin_indexes
)

from .mixins import (
    GroupingMixin, NamedMixin,
    create_division_field, create_types_field
)
from .geometry import WithGeometryMixin


class Route(NamedMixin, WithGeometryMixin, CodesDefinableMixin, GroupingMixin):
    class Meta:
        verbose_name = pgettext_lazy('wcd_geo_db:route', 'Route')
        verbose_name_plural = pgettext_lazy('wcd_geo_db:route', 'Routes')

    id = models.BigAutoField(
        primary_key=True, verbose_name=pgettext_lazy('wcd_geo_db:route', 'ID')
    )
    types = create_types_field(pgettext_lazy('wcd_geo_db:route', 'Route types'))
    division = create_division_field()
