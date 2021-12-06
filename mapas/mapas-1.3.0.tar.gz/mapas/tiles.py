from typing import Tuple
import math

from .vector import div, sub, add, ceil, mul

# source: https://www.iogp.org/wp-content/uploads/2019/09/373-07-02.pdf
ELLIPSOID_SEMIMAJOR_AXIS = 6378137.0  # in metres
CIRCUMFERENCE_AT_EQUATOR = 40075016.68557849  # in metres


def tiles_to_cover(
        dimensions: Tuple[int, int], tile_size: int,
        center_tile_offset: Tuple[int, int]) -> Tuple[int, int]:
    ''' returns a tuple indicating how many tiles we need in both axes to cover
    the specified area '''
    tile_corner = sub(div(dimensions, 2), center_tile_offset)

    tiles_to_cover_topleft = ceil(div(tile_corner, tile_size))
    tiles_to_cover_botright = ceil(div(sub(dimensions, tile_corner), tile_size))

    return add(tiles_to_cover_topleft, tiles_to_cover_botright)


def topleft_tile(
        dimensions: Tuple[int, int], tile_size: int, zoom: int,
        center: Tuple[float, float], center_tile_offset: Tuple[int, int]) -> Tuple[int, int]:
    tile_corner = sub(div(dimensions, 2), center_tile_offset)

    tiles_to_cover_topleft = ceil(div(tile_corner, tile_size))
    center_tile = coordinates_to_tile_number(zoom, center[1], center[0])

    return sub(center_tile, tiles_to_cover_topleft)


def topleft_coords(
        dimensions: Tuple[int, int], tile_size: int,
        center_tile_offset: Tuple[int, int]) -> Tuple[int, int]:
    tile_corner = sub(div(dimensions, 2), center_tile_offset)
    tiles_to_cover_topleft = ceil(div(tile_corner, tile_size))

    return sub(tile_corner, mul(tiles_to_cover_topleft, tile_size))

# stolen from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
#
# returns (x, y) pair


def coordinates_to_tile_and_fraction(
        z: int, lat: float, lon: float) -> Tuple[float, float]:
    lat_rad = math.radians(lat)
    n = 2.0 ** z
    xtile = (lon + 180.0) / 360.0 * n
    ytile = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
    return (xtile, ytile)


def coordinates_to_tile_number(
        z: int, lat: float, lon: float) -> Tuple[int, int]:
    (xtile, ytile) = coordinates_to_tile_and_fraction(z, lat, lon)
    return (int(xtile), int(ytile))


def tile_number_to_coordinates(
        z: int, xtile: int, ytile: int) -> Tuple[float, float]:
    n = 2.0 ** z
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = lat_rad * 180.0 / math.pi
    return (lat_deg, lon_deg)


def compute_real_world_m_per_tile(
        latitude: float, zoom: int) -> float:
    lat_rad = math.radians(latitude)

    meridian_length = CIRCUMFERENCE_AT_EQUATOR * math.cos(lat_rad)
    tiles_around_the_earth = 2 ** zoom

    m_per_tile = meridian_length / tiles_around_the_earth
    return m_per_tile


def lon_lat_to_web_merkator(lon: float, lat: float) -> Tuple[float, float]:
    return (
        ELLIPSOID_SEMIMAJOR_AXIS * math.radians(lon),
        ELLIPSOID_SEMIMAJOR_AXIS * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    )


def compute_real_world_m_per_px(
        latitude: float, zoom: int, tile_size: int = 256) -> float:
    return compute_real_world_m_per_tile(latitude, zoom) / tile_size


def get_tile_offset(
        tile_size: int, zoom: int, center: Tuple[float, float]) -> Tuple[int, int]:
    xtile, ytile = coordinates_to_tile_and_fraction(zoom, center[1], center[0])
    xtile = xtile % 1
    ytile = ytile % 1

    return (int(xtile * tile_size), int(ytile * tile_size))
