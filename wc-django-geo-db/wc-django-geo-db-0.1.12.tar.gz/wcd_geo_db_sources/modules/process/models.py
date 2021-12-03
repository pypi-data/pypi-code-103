from typing import Sequence, Type
from django.db import models
from django.utils.translation import pgettext_lazy

from .const import ProcessStatus, ProcessStage
from .query import ProcessStateQuerySet


__all__ = 'ProcessState', 'ProcessSourceConfig',

class ProcessState(models.Model):
    Status: Type[ProcessStatus] = ProcessStatus
    Stage: ProcessStage = ProcessStage
    objects: models.Manager[ProcessStateQuerySet] = ProcessStateQuerySet.as_manager()

    class Meta:
        verbose_name = pgettext_lazy('wcd_geo_db_sources:process', 'Process state')
        verbose_name_plural = pgettext_lazy('wcd_geo_db_sources:process', 'Process states')

    id = models.BigAutoField(
        primary_key=True, verbose_name=pgettext_lazy('wcd_geo_db_sources:process', 'ID')
    )
    source = models.CharField(
        verbose_name=pgettext_lazy('wcd_geo_db_sources:process', 'Source name'),
        max_length=512, null=False, blank=False,
    )
    status = models.CharField(
        verbose_name=pgettext_lazy('wcd_geo_db_sources:process', 'Status'),
        max_length=32, choices=Status.choices, default=Status.NEW,
        null=False, blank=False,
    )
    stage = models.CharField(
        verbose_name=pgettext_lazy('wcd_geo_db_sources:process', 'Stage'),
        max_length=32, default=Stage.INITIAL, null=False, blank=False,
    )
    state = models.JSONField(
        verbose_name=pgettext_lazy('wcd_geo_db_sources:process', 'State'),
        null=False, blank=True, default=dict
    )

    version = models.PositiveIntegerField(
        verbose_name=pgettext_lazy('wcd_geo_db_sources:process', 'Version'),
        editable=False, null=False, blank=False, default=1
    )

    def __str__(self):
        return f'Import process #{self.id} for "{self.source}"'

    def versioned_save(self, fields: Sequence[str]):
        current = self.version
        self.version += 1
        saved = (
            self.__class__.objects
            .filter(id=self.id, version=current)
            .update(**{
                **{
                    field: getattr(self, field) for field in fields
                },
                'version': self.version
            })
        )

        return saved == 1


class ProcessSourceConfig(models.Model):
    class Meta:
        verbose_name = pgettext_lazy('wcd_geo_db_sources:process', 'Process source config')
        verbose_name_plural = pgettext_lazy('wcd_geo_db_sources:process', 'Process source configs')

    id = models.AutoField(
        primary_key=True, verbose_name=pgettext_lazy('wcd_geo_db_sources:process', 'ID')
    )
    source = models.CharField(
        verbose_name=pgettext_lazy('wcd_geo_db_sources:process', 'Source name'),
        max_length=512, null=False, blank=False, unique=True
    )
    config = models.JSONField(
        verbose_name=pgettext_lazy('wcd_geo_db_sources:process', 'Configuration'),
        null=False, blank=True, default=dict
    )

    def __str__(self):
        return f'Configuration for "{self.source}" source'
