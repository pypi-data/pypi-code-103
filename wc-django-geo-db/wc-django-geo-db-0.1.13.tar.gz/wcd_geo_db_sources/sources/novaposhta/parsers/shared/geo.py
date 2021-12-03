from typing import List, Optional, Sequence
from wcd_geo_db_sources.modules.merger.dtos import DivisionItem, DivisionTranslationItem

from .mappings import (
    get_category_types,
    get_code_types,
    get_level_types,
    get_category_level,
    get_hierarchy_level,
    get_type_levels
)


__all__ = (
    'Geo', 'geo_order_key',
    'get_types', 'get_level', 'update_geo',
)


class Geo(DivisionItem):
    translations: List[DivisionTranslationItem]


def geo_order_key(geo: Geo):
    return (len(geo['path']), geo['code'])


def get_types(geo: Geo):
    return (
        get_category_types(geo['category']) | get_code_types(geo['code'][1])
    )


def get_level(geo: Geo):
    level = get_category_level(geo['category'])

    if level is None:
        level = min((
            get_hierarchy_level(len(geo['path']) + 1),
            *get_type_levels(geo['types'])
        ))

    return level


def update_geo(geo: Geo) -> Geo:
    # geo['types'] = get_types(geo)
    # geo['level'] = get_level(geo)
    # geo['types'].update(get_level_types(geo['level']))

    return geo
