from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ('GeoDBConfig',)


class GeoDBConfig(AppConfig):
    name = 'wcd_geo_db'
    verbose_name = pgettext_lazy('wcd_geo_db', 'Geographical database')
