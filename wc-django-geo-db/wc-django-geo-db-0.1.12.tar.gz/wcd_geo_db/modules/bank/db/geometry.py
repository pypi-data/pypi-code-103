from django.db import models
from django.contrib.gis.db import models as geo_models
from django.utils.translation import pgettext_lazy


__all__ = 'Geometry', 'WithGeometryMixin',


SRID = 4326


class Geometry(models.Model):
    class Meta:
        verbose_name = pgettext_lazy('wcd_geo_db:geometry', 'Geometry')
        verbose_name_plural = pgettext_lazy('wcd_geo_db:geometry', 'Geometries')

    id = models.BigAutoField(
        primary_key=True, verbose_name=pgettext_lazy('wcd_geo_db:geometry', 'ID')
    )
    location = geo_models.PointField(
        verbose_name=pgettext_lazy('wcd_geo_db:geometry', 'Location'),
        srid=SRID, geography=True, spatial_index=True,
        null=True, blank=False
    )
    polygon = geo_models.PolygonField(
        verbose_name=pgettext_lazy('wcd_geo_db:geometry', 'Polygon'),
        srid=SRID, geography=True, spatial_index=True,
        null=True, blank=True
    )

    def __str__(self):
        return str(self.location)


class WithGeometryMixin(models.Model):
    class Meta:
        abstract = True

    geometry = models.ForeignKey(
        Geometry,
        verbose_name=pgettext_lazy('wcd_geo_db:field', 'Geometry'),
        null=True, blank=True, on_delete=models.SET_NULL
    )
