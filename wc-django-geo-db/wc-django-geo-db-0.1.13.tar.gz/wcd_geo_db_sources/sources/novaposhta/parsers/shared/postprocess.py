from typing import Dict, List, Set
from wcd_geo_db.const import DivisionLevel, DivisionType

from .geo import Geo
from .categories import Category


__all__ = 'Hierarchy', 'collect_hierarchy', 'postprocess_items',

Hierarchy = Dict[str, Set[str]]


def collect_hierarchy(items: List[Geo]) -> Hierarchy:
    hierarchy: Hierarchy = {}

    for geo in items:
        parent = None

        for code, item in (geo['path'] + [geo['code']]):
            if parent is not None:
                hierarchy[parent] = hierarchy.get(parent) or set()
                hierarchy[parent].add(item)

            parent = item

    return hierarchy


def safe_remove(items: set, value) -> set:
    if value in items:
        items.remove(value)

    return items


def postprocess_items(items: List[Geo], hierarchy: Hierarchy) -> List[Geo]:
    index_map = {
        item['code'][1]: index
        for index, item in enumerate(items)
    }
    for item in items:
        if item['level'] != DivisionLevel.LOCALITY:
            # Fixing all cities with city districts inside that
            # are marked in some other way.
            for code in hierarchy.get(item['code'][1], []):
                if code not in index_map:
                    # Happens to be that there are no elements in the path.
                    # Strange, but anyway.
                    continue

                if items[index_map[code]]['level'] in {
                    DivisionLevel.SUBLOCALITY_LEVEL_1,
                    DivisionLevel.SUBLOCALITY_LEVEL_2,
                    DivisionLevel.SUBLOCALITY_LEVEL_3,
                }:
                    item['category'] = Category.CITY
                    item['level'] = DivisionLevel.LOCALITY
                    safe_remove(item['types'], DivisionType.REGION)
                    safe_remove(item['types'], DivisionType.DISTRICT)
                    safe_remove(item['types'], DivisionType.MUNICIPALITY)
                    safe_remove(item['types'], DivisionType.COMMUNE)
                    safe_remove(item['types'], DivisionType.COMMUNITY)
                    item['types'].add(DivisionType.LOCALITY)
                    item['types'].add(DivisionType.CITY)

    return items
