from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import pgettext_lazy


__all__ = (
    'create_types_field', 'create_division_field',
    'GroupingMixin', 'NamedMixin',
)


def create_types_field(verbose_name):
    return ArrayField(
        base_field=models.CharField(max_length=512),
        verbose_name=verbose_name,
        null=False, blank=True, default=list
    )


def create_division_field(**kw):
    return models.ForeignKey(
        'Division',
        **{
            **dict(
                verbose_name = pgettext_lazy('wcd_geo_db:field', 'Division'),
                null=True, on_delete=models.SET_NULL, blank=False
            ),
            **kw
        }
    )


class GroupingMixin(models.Model):
    class Meta:
        abstract = True

    grouping = models.ForeignKey(
        'self',
        verbose_name=pgettext_lazy('wcd_geo_db', 'Grouping entity'),
        on_delete=models.SET_NULL, null=True, blank=True, default=None
    )


class NamedMixin(models.Model):
    class Meta:
        abstract = True

    name = models.TextField(
        verbose_name=pgettext_lazy('wcd_geo_db', 'Name')
    )

    def __str__(self):
        return self.name


class SynonymizedMixin(models.Model):
    class Meta:
        abstract = True

    synonyms = models.TextField(
        verbose_name=pgettext_lazy('wcd_geo_db', 'Synonyms'),
        null=False, blank=True, default=''
    )
