from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ('GeoDBDalConfig',)


class GeoDBDalConfig(AppConfig):
    name = 'wcd_geo_db.contrib.dal'
    label = 'wcd_geo_db_dal'
    verbose_name = pgettext_lazy('wcd_geo_db:dal', 'Geographical database: Dal')
