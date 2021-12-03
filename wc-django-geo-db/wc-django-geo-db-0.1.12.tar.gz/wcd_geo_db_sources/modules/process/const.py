from django.db import models
from django.utils.translation import pgettext_lazy


__all__ = 'ProcessStatus', 'ProcessStage'


class ProcessStatus(models.TextChoices):
    NEW = '001000-new', pgettext_lazy('wcd_geo_db_sources:process', 'New')
    IN_PROGRESS = '001500-in-progress', pgettext_lazy('wcd_geo_db_sources:process', 'In progress')
    FAILED = '009800-new', pgettext_lazy('wcd_geo_db_sources:process', 'Failed')
    SUCCESS = '009900-new', pgettext_lazy('wcd_geo_db_sources:process', 'Success')


class ProcessStage(models.TextChoices):
    INITIAL = '001000-initial', pgettext_lazy('wcd_geo_db_sources:process', 'Initial')
