from mapas.tiles import (
    coordinates_to_tile_number, coordinates_to_tile_and_fraction,
    tile_number_to_coordinates,
)

from .testutils import float_equals


def test_tile_number_and_fraction_roundtrips_to_coordinates():
    start_lat = 19.4621106
    start_lon = -96.9040473

    for zoom in range(0, 20):
        (tile_x, tile_y) = coordinates_to_tile_and_fraction(zoom, start_lat, start_lon)
        (end_lat, end_lon) = tile_number_to_coordinates(zoom, tile_x, tile_y)

        assert float_equals(start_lat, end_lat)
        assert float_equals(start_lon, end_lon)


def test_cerro_malinche_is_in_the_correct_tile():
    lat = 19.4621106
    lon = -96.9040473
    zoom = 15

    expected_tile_x = 7563
    expected_tile_y = 14577

    (tile_x, tile_y) = coordinates_to_tile_number(zoom, lat, lon)

    assert float_equals(tile_x, expected_tile_x)
    assert float_equals(tile_y, expected_tile_y)
