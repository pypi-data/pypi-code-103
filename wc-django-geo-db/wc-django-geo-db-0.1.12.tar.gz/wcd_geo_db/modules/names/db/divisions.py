from django.db import models
from django.utils.translation import pgettext_lazy

from wcd_geo_db.const import DivisionLevel

from wcd_geo_db.modules.bank.db.mixins import NamedMixin, create_division_field


__all__ = 'DivisionName',


class DivisionName(NamedMixin, models.Model):
    Levels = DivisionLevel

    class Meta:
        verbose_name = pgettext_lazy('wcd_geo_db:names', 'Division name')
        verbose_name_plural = pgettext_lazy('wcd_geo_db:names', 'Division names')
        unique_together = (
            ('country_id', 'level'),
        )

    id = models.BigAutoField(
        primary_key=True, verbose_name=pgettext_lazy('wcd_geo_db', 'ID')
    )
    level = models.SmallIntegerField(
        verbose_name=pgettext_lazy('wcd_geo_db', 'Division level'),
        choices=Levels.choices, null=False, blank=False
    )
    country = create_division_field(
        null=False, on_delete=models.CASCADE,
        limit_choices_to={'level': Levels.COUNTRY}
    )
