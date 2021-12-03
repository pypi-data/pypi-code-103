from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ('GeoDBAdminConfig',)


class GeoDBAdminConfig(AppConfig):
    name = 'wcd_geo_db.contrib.admin'
    label = 'wcd_geo_db_admin'
    verbose_name = pgettext_lazy('wcd_geo_db:admin', 'Geographical database: Admin')
