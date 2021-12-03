from typing import Dict, Optional, Sequence
from django.contrib.postgres.indexes import BTreeIndex, GinIndex
from django.db import models
from django.utils.translation import pgettext_lazy, pgettext


__all__ = (
    'CODES_POSTFIX',
    'CODES_RELATED_NAME',
    'codes_indexes',
    'create_codes_model',
    'codes_mixin_indexes',
    'CodesDefinableMixin',
)

EMPTY = object()
CODES_POSTFIX: str = 'Code'
CODES_RELATED_NAME: str = 'codes_set'


def codes_indexes(name: str = '%(app_label)s_%(class)s'):
    return [
        BTreeIndex(
            name=name + '_cds_idx',
            fields=['code', 'value'],
        ),
    ]


def collect_model_fields(model: models.Model, fields: Sequence[str]) -> Dict[str, models.Field]:
    return {
        field: model._meta.get_field(field).clone()
        for field in fields
    }


def create_codes_model(
    model: models.Model,
    postfix: str = CODES_POSTFIX,
    related_name: str = CODES_RELATED_NAME,
    verbose_name: Optional[str] = None,
    verbose_name_plural: Optional[str] = None,
    abstract: bool = False
) -> models.Model:
    base_name = model.__name__
    name = base_name  + postfix

    Meta = type('Meta', (), {
        key: value
        for key, value in (
            ('verbose_name', verbose_name),
            ('verbose_name_plural', verbose_name_plural),
            ('abstract', abstract),
            ('indexes', codes_indexes()),
        )
        if value
    })

    class CodeModel(models.Model):
        class Meta:
            abstract = True

        id = models.BigAutoField(
            primary_key=True, verbose_name=pgettext_lazy('wcd_geo_db:codes', 'ID')
        )
        code = models.TextField(
            verbose_name=pgettext_lazy('wcd_geo_db:codes', 'Code'),
            null=False, blank=False,
        )
        value = models.TextField(
            verbose_name=pgettext_lazy('wcd_geo_db:codes', 'Value'),
            null=False, blank=False,
        )
        entity = models.ForeignKey(
            model,
            verbose_name=pgettext_lazy('wcd_geo_db:codes', 'Code entity'),
            null=False, blank=False, on_delete=models.CASCADE,
            related_name=related_name
        )

        def __str__(self):
            return (
                pgettext('wcd_geo_db:codes', '#{entity_id} "{code}":"{value}"')
                .format(value=self.value, code=self.code, entity_id=self.entity_id)
            )

    return type(name, (CodeModel,), {
        '__module__': model.__module__,
        'Meta': Meta,
    })



def codes_mixin_indexes():
    return [
        GinIndex(
            name='%(app_label)s_%(class)s_codes_idx',
            fields=['codes'],
            opclasses=('jsonb_ops',)
        ),
    ]


class CodesDefinableMixin(models.Model):
    class Meta:
        abstract = True

    codes = models.JSONField(
        verbose_name=pgettext_lazy('wcd_geo_db:codes', 'Codes'),
        null=False, blank=True, default=dict, editable=False
    )
