#
#   Test IO functionality
#
import pandas as pd
import geopandas as gpd
import geopandas.testing
import shapely
import shapely.geometry
import pgpd                     # noqa: F401


def test_shapely():
    data = pd.Series([
        shapely.geometry.Point((10, 20)),
        shapely.geometry.LineString([(0, 0), (15, 10)]),
        shapely.geometry.Polygon([(-5, -5), (0, 0), (-5, 5), (-10, 0)]),
        None,
    ])

    geos_data = data.geos.to_geos()
    result = geos_data.geos.to_shapely()

    pd.testing.assert_series_equal(data, result, check_names=False)


def test_wkt():
    data = pd.Series([
        'POINT (10 20)',
        'LINESTRING (0 0, 15 10)',
        'POLYGON ((-5 -5, 0 0, -5 5, -10 0, -5 -5))',
        None,
    ])

    geos_data = data.geos.to_geos()
    result = geos_data.geos.to_wkt()

    pd.testing.assert_series_equal(data, result, check_names=False)


def test_wkb():
    data = pd.Series([
        b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00$@\x00\x00\x00\x00\x00\x004@',
        b'\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00.@\x00\x00\x00\x00\x00\x00$@',
        b'\x01\x03\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\xc0\x00\x00\x00\x00\x00\x00\x14\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\xc0\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00$\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\xc0\x00\x00\x00\x00\x00\x00\x14\xc0',  # noqa: B950
        None,
    ])

    geos_data = data.geos.to_geos()
    result = geos_data.geos.to_wkb()

    pd.testing.assert_series_equal(data, result, check_names=False)


def test_geopandas():
    data = gpd.GeoSeries([
        shapely.geometry.Point((10, 20)),
        shapely.geometry.LineString([(0, 0), (15, 10)]),
        shapely.geometry.Polygon([(-5, -5), (0, 0), (-5, 5), (-10, 0)]),
        None,
    ])

    geos_data = data.geos.to_geos()
    result = geos_data.geos.to_geopandas()

    gpd.testing.assert_geoseries_equal(data, result)


def test_geopandas_df():
    data = gpd.GeoDataFrame({
        'extra': [1, 2, 3, 4],
        'geometry': [
            shapely.geometry.Point((10, 20)),
            shapely.geometry.LineString([(0, 0), (15, 10)]),
            shapely.geometry.Polygon([(-5, -5), (0, 0), (-5, 5), (-10, 0)]),
            None,
        ],
    })

    geos_data = data.geos.to_geos()
    result = geos_data.geos.to_geopandas()

    gpd.testing.assert_geodataframe_equal(data, result)
