#
#   Test if all pygeos methods are implemented
#   This makes it easier to update PGPD to new PyGEOS versions
#
import pytest
import pygeos
import pgpd

skips = {
    'geometry': (
        'IntEnum',
        'SetPrecisionMode',
    ),
    'creation': (
        'box',
        'collections_1d',
        'empty',
        'geometrycollections',
        'linearrings',
        'linestrings',
        'multilinestrings',
        'multipoints',
        'multipolygons',
        'points',
        'polygons',
        'simple_geometries_1d',
    ),
    'measurement': (),
    'predicates': (
        'warnings',
    ),
    'set_operations': (
        'box',
        'UnsupportedGEOSOperation',
    ),
    'constructive': (
        'BufferCapStyles',
        'BufferJoinStyles',
        'polygonize_full',
    ),
    'linear': (
        'warn',
    ),
    'coordinates': (
        'get_coordinates',
    ),
    'strtree': (
        'BinaryPredicate',
        'VALID_PREDICATES',
    ),
}

global_skips = (
    'Geometry',
    'GeometryType',
    'geos_version',
    'lib',
    'multithreading_enabled',
    'np',
    'ParamEnum',
    'requires_geos',
    'warnings',
)


@pytest.mark.parametrize('module', skips.keys())
def test_for_missing_methods(module):
    skip = skips[module]
    mod = getattr(pygeos, module)

    for func in dir(mod):
        if func.startswith('_'):
            continue
        if func in global_skips:
            continue
        if func in skip:
            continue

        if func not in dir(pgpd.GeosSeriesAccessor):
            raise NotImplementedError(f'{module}.{func}')
