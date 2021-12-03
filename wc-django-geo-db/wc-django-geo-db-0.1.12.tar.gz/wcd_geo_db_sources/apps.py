from django.apps import AppConfig
from django.utils.translation import pgettext_lazy

from .discover import autodiscover


__all__ = ('GeoDBSourcesConfig',)


class GeoDBSourcesConfig(AppConfig):
    name = 'wcd_geo_db_sources'
    verbose_name = pgettext_lazy('wcd_geo_db_sources', 'Geographical database sources')

    def ready(self):
        autodiscover()
