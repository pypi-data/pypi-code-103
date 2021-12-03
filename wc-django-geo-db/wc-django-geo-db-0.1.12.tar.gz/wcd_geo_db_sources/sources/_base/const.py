from django.utils.translation import pgettext_lazy
from django.db import models

from wcd_geo_db_sources.modules.process import ProcessStage


__all__ = 'BaseImportStage',


class BaseImportStage(models.TextChoices):
    INITIAL = ProcessStage.INITIAL
    UPLOADING = '002000-uploading', pgettext_lazy('wcd_geo_db_sources:source', 'Uploading')
    PARSING = '003000-parsing', pgettext_lazy('wcd_geo_db_sources:source', 'Parsing')
    MERGE = '004000-merge', pgettext_lazy('wcd_geo_db_sources:source', 'Merge')
    MERGE_TRANSLATIONS = '004500-merge-translations', pgettext_lazy('wcd_geo_db_sources:source', 'Merge translations')
    CLEANUP = '005000-cleanup', pgettext_lazy('wcd_geo_db_sources:source', 'Cleanup')
