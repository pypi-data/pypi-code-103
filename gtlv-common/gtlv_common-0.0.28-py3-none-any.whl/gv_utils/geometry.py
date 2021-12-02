#!/usr/bin/env python3

import math
from typing import Generator, Iterable, List, Tuple, Union

import shapely.geometry
from shapely.geometry.base import BaseGeometry
import shapely.ops
import shapely.wkb
import shapely.wkt

LONLAT_CENTER = (5.74626, 45.17475)
LONLAT_EXTEND = ((5.60268, 45.0821), (5.88934, 45.2674))
EXTEND_BBOX_XY = None
SRID = 4326
R = 6371000  # earth radius in meters
ONE_METER_IN_LATLON = .0000128


def geom_to_xy(geom: BaseGeometry, lonlatcenter: Tuple[float, float] = None, rounding: int = 2) -> BaseGeometry:
    if lonlatcenter is None:
        lonlatcenter = LONLAT_CENTER

    return shapely.ops.transform(lambda lon, lat, z=None: _to_xy(lon, lat, lonlatcenter, rounding), geom)


def lonlat_to_xy(lonlat: Tuple[float, float], lonlatcenter: Tuple[float, float] = None,
                 rounding: int = 2) -> Tuple[float, float]:
    if lonlatcenter is None:
        lonlatcenter = LONLAT_CENTER

    return _to_xy(*lonlat, lonlatcenter=lonlatcenter, rounding=rounding)


def coords_to_xy(coords: Iterable[Tuple[float, float]], lonlatcenter: Tuple[float, float] = None,
                 rounding: int = 2) -> Generator[Tuple[float, float], None, None]:
    if lonlatcenter is None:
        lonlatcenter = LONLAT_CENTER

    for lonlat in coords:
        yield _to_xy(*lonlat, lonlatcenter=lonlatcenter, rounding=rounding)


def _to_xy(lon: float, lat: float, lonlatcenter: Tuple[float, float], rounding: int) -> Tuple[float, float]:
    if rounding is not None:
        _f = lambda u: round(u, rounding)
    else:
        _f = lambda u: u

    lon = lon * math.pi / 180
    lat = lat * math.pi / 180
    loncenter = lonlatcenter[0] * math.pi / 180
    latcenter = lonlatcenter[1] * math.pi / 180

    x = R * math.cos(lat) * math.sin(lon - loncenter)
    y = R * (math.cos(latcenter) * math.sin(lat) - math.sin(latcenter) * math.cos(lat) * math.cos(lon - loncenter))
    return _f(x), _f(y)


def geom_to_lonlat(geom: BaseGeometry, lonlatcenter: Tuple[float, float] = None, rounding: int = 5) -> BaseGeometry:
    if lonlatcenter is None:
        lonlatcenter = LONLAT_CENTER

    return shapely.ops.transform(lambda x, y, z=None: _to_lonlat(x, y, lonlatcenter, rounding), geom)


def xy_to_lonlat(x: float, y: float, lonlatcenter: Tuple[float, float] = None,
                 rounding: int = 5) -> Tuple[float, float]:
    if lonlatcenter is None:
        lonlatcenter = LONLAT_CENTER

    return _to_lonlat(x, y, lonlatcenter, rounding)


def coords_to_lonlat(coords: List[Tuple[float, float]], lonlatcenter: Tuple[float, float] = None,
                     rounding: int = 5) -> Generator[Tuple[float, float], None, None]:
    if lonlatcenter is None:
        lonlatcenter = LONLAT_CENTER

    for xy in coords:
        yield _to_lonlat(*xy, lonlatcenter=lonlatcenter, rounding=rounding)


def _to_lonlat(x: float, y: float, lonlatcenter: Tuple[float, float], rounding: int) -> Tuple[float, float]:
    if rounding is not None:
        _f = lambda u: round(u, rounding)
    else:
        _f = lambda u: u

    loncenter = lonlatcenter[0] * math.pi / 180
    latcenter = lonlatcenter[1] * math.pi / 180

    p = math.pow(x ** 2 + y ** 2, .5)
    c = math.asin(p / R)

    lon = loncenter + math.atan2(x * math.sin(c),
                                 p * math.cos(c) * math.cos(latcenter) - y * math.sin(c) * math.sin(latcenter))
    lat = math.asin(math.cos(c) * math.sin(latcenter) + y * math.sin(c) * math.cos(latcenter) / p)
    lon = lon / math.pi * 180
    lat = lat / math.pi * 180
    return _f(lon), _f(lat)


def round_lonlat(lonlat: Tuple[float, float]) -> Tuple[int, int]:
    return round(lonlat[0] * 1000), round(lonlat[1] * 1000)


def shift_to_right(geom: shapely.geometry.LineString, dist: int) -> shapely.geometry.LineString:
    geom = geom.parallel_offset(dist, 'right')
    geom.coords = list(geom.coords)[::-1]
    return geom


def is_inside_extend(geomxy: BaseGeometry) -> bool:
    global EXTEND_BBOX_XY
    if EXTEND_BBOX_XY is None:
        coords = []
        for coord in coords_to_xy(LONLAT_EXTEND):
            coords.extend(coord)
        EXTEND_BBOX_XY = shapely.geometry.box(*coords)

    return EXTEND_BBOX_XY.intersects(geomxy)


def close_elems_it(lonlatrounded: Tuple[int, int], lonlatmatrix: dict,
                   radius: int = 1) -> Generator[BaseGeometry, None, None]:
    if radius >= 1:
        lat, lon = lonlatrounded
        for i in _get_range(lat, radius):
            if i in lonlatmatrix:
                for j in _get_range(lon, radius):
                    if j in lonlatmatrix[i]:
                        for elem in lonlatmatrix[i][j]:
                            yield elem


def _get_range(i: int, radius: int) -> List[int]:
    return sorted(range(i - radius, i + radius + 1), key=lambda x: abs(x - i))


def encode_geometry(geometry: Union[BaseGeometry, str]) -> str:
    if not isinstance(geometry, str):
        geometry = shapely.wkt.dumps(geometry)
    return '{};{}'.format('SRID={}'.format(SRID), geometry)


def encode_geometry_bytes(geometry: Union[BaseGeometry, str]) -> str:
    if not isinstance(geometry, BaseGeometry):
        geometry = decode_geometry(geometry)
    return shapely.wkb.dumps(geometry, srid=SRID)


def decode_geometry(wkt: str) -> BaseGeometry:
    geom = None
    try:
        geom = shapely.wkt.loads(wkt.split(';')[-1])
    except:
        try:
            geom = shapely.geometry.shape(wkt)
        except:
            pass
    return geom


def decode_geometry_bytes(wkb: bytes) -> BaseGeometry:
    geom = None
    try:
        geom = shapely.wkb.loads(wkb)
    except:
        pass
    return geom
