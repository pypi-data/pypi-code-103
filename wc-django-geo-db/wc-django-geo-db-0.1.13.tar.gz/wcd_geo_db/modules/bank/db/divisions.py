from django.db import models
from django.contrib.postgres.indexes import GistIndex
from django.utils.translation import pgettext_lazy

from pxd_tree.hierarchy import Tree, tree_indexes
from wcd_geo_db.const import DivisionLevel
from wcd_geo_db.modules.code_seeker.models import (
    create_codes_model, CodesDefinableMixin, codes_mixin_indexes
)

from ..query import DivisionsQuerySet
from .mixins import NamedMixin, SynonymizedMixin, create_types_field
from .geometry import WithGeometryMixin


__all__ = 'Division', 'DivisionCode',


class Division(Tree, NamedMixin, SynonymizedMixin, WithGeometryMixin, CodesDefinableMixin):
    Levels = DivisionLevel
    objects: models.Manager[DivisionsQuerySet] = DivisionsQuerySet.as_manager()

    class Meta:
        verbose_name = pgettext_lazy('wcd_geo_db', 'Division')
        verbose_name_plural = pgettext_lazy('wcd_geo_db', 'Divisions')
        indexes = tree_indexes() + codes_mixin_indexes() + [
            GistIndex(
                name='%(app_label)s_%(class)s_name_idx',
                fields=['name'],
                opclasses=['gist_trgm_ops'],
            ),
            GistIndex(
                name='%(app_label)s_%(class)s_syn_idx',
                fields=['synonyms'],
                opclasses=['gist_trgm_ops'],
            ),
        ]

    id = models.BigAutoField(
        primary_key=True, verbose_name=pgettext_lazy('wcd_geo_db', 'ID')
    )
    level = models.SmallIntegerField(
        verbose_name=pgettext_lazy('wcd_geo_db', 'Division level'),
        choices=Levels.choices, null=False, blank=False
    )
    types = create_types_field(pgettext_lazy('wcd_geo_db', 'Division types'))


DivisionCode = create_codes_model(
    Division,
    verbose_name=pgettext_lazy('wcd_geo_db', 'Division code'),
    verbose_name_plural=pgettext_lazy('wcd_geo_db', 'Division codes'),
)
