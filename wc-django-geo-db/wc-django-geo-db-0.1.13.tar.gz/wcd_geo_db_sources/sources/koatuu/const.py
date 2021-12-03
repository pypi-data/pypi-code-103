from django.utils.translation import pgettext_lazy
from django.db import models

from wcd_geo_db_sources.modules.process import ProcessStage

from .._base import BaseImportStage


__all__ = 'SOURCE', 'ImportStage'

SOURCE = 'KOATUU'

ImportStage = BaseImportStage
