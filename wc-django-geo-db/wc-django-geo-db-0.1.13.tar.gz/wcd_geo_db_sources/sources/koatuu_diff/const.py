from django.db import models
from django.utils.translation import pgettext_lazy

from .._base import BaseImportStage


__all__ = 'SOURCE', 'ImportStage'

SOURCE = 'KOATUU_DIFF'


class ImportStage(models.TextChoices):
    INITIAL = BaseImportStage.INITIAL
    UPLOADING = BaseImportStage.UPLOADING
    PARSING = BaseImportStage.PARSING
    DIFF = '003500-diff', pgettext_lazy('wcd_geo_db_sources:source', 'Diff')
    PREPARE_DIFF = '003550-prepare-diff', pgettext_lazy('wcd_geo_db_sources:source', 'Prepare diff')
    MERGE = BaseImportStage.MERGE
    MERGE_TRANSLATIONS = BaseImportStage.MERGE_TRANSLATIONS
    CLEANUP = BaseImportStage.CLEANUP
