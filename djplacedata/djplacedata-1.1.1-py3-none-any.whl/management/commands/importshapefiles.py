from django.contrib.gis.geos import MultiPolygon, Polygon
from django.contrib.gis.gdal.datasource import DataSource
from django.core.management.base import BaseCommand

from census_shapefiles import CensusShapefiles

from djplacedata.models import Place


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('year', type=int)
        parser.add_argument(
            '--simplification',
            default=0,
        )

    def handle(self, *args, **options):
        year = options['year']
        self.simplification = options['simplification']

        shapefiles = CensusShapefiles(year)

        for shapefile in shapefiles.state.get_shapefiles():
            ds = DataSource(shapefile)
            for feature in ds[0]:
                Place.objects.update_or_create(
                    geoid=feature.get('GEOID'),
                    defaults={
                        'name': feature.get('NAME'),
                        'geom': self._transform(feature.geom.geos),
                        'type': Place.Type.state
                    })

        for shapefile in shapefiles.county.get_shapefiles():
            ds = DataSource(shapefile)
            for feature in ds[0]:
                state_geoid = feature.get('GEOID')[:2]
                Place.objects.update_or_create(
                    geoid=feature.get('GEOID'),
                    defaults={
                        'name': feature.get('NAME'),
                        'geom': self._transform(feature.geom.geos),
                        'parent': Place.objects.get(geoid=state_geoid),
                        'type': Place.Type.county,
                    })

        for shapefile in shapefiles.city.get_shapefiles():
            ds = DataSource(shapefile)
            for feature in ds[0]:
                county_geoid = feature.get('GEOID')[:5]
                Place.objects.update_or_create(
                    geoid=feature.get('GEOID'),
                    defaults={
                        'name': feature.get('NAME'),
                        'geom': self._transform(feature.geom.geos),
                        'parent': Place.objects.get(geoid=county_geoid),
                        'type': Place.Type.city,
                    })

        for shapefile in shapefiles.tract.get_shapefiles():
            ds = DataSource(shapefile)
            for feature in ds[0]:
                county_geoid = feature.get('GEOID')[:5]
                Place.objects.update_or_create(
                    geoid=feature.get('GEOID'),
                    defaults={
                        'name': feature.get('NAME'),
                        'geom': self._transform(feature.geom.geos),
                        'parent': Place.objects.get(geoid=county_geoid),
                        'type': Place.Type.tract,
                    }
                )

    def _transform(self, shape):
        shape = shape.simplify(tolerance=self.simplification, preserve_topology=True)
        if isinstance(shape, MultiPolygon):
            return shape
        elif isinstance(shape, Polygon):
            return MultiPolygon(shape)
        else:
            raise Exception()
