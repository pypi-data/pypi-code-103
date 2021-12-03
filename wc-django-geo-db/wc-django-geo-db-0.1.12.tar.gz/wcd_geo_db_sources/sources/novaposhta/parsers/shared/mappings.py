from typing import Set
from wcd_geo_db.const import DivisionLevel, DivisionType

from .categories import Category


__all__ = (
    'get_code_types',
    'get_category_types',
    'get_level_types',
    'get_category_level',
    'get_hierarchy_level',
    'get_type_levels',
)

CATEGORY_TYPES = {
    None: {},
    Category.CITY: {DivisionType.LOCALITY, DivisionType.CITY},
    Category.CITY_DISTRICT: {DivisionType.CITY_DISTRICT},
    Category.TOWN: {DivisionType.LOCALITY, DivisionType.TOWN},
    Category.VILLAGE: {DivisionType.LOCALITY, DivisionType.VILLAGE},
    Category.HAMLET: {DivisionType.LOCALITY,DivisionType.HAMLET},
}
CATEGORY_LEVELS = {
    Category.CITY: DivisionLevel.LOCALITY,
    Category.CITY_DISTRICT: DivisionLevel.SUBLOCALITY_LEVEL_1,
    Category.TOWN: DivisionLevel.LOCALITY,
    Category.VILLAGE: DivisionLevel.LOCALITY,
    Category.HAMLET: DivisionLevel.LOCALITY,
}
LEVELS_TYPES = {
    DivisionLevel.ADMINISTRATIVE_LEVEL_1: {DivisionType.REGION},
    DivisionLevel.ADMINISTRATIVE_LEVEL_2: {DivisionType.DISTRICT, DivisionType.MUNICIPALITY},
    DivisionLevel.ADMINISTRATIVE_LEVEL_3: {DivisionType.COMMUNE, DivisionType.COMMUNITY},
    DivisionLevel.LOCALITY: {DivisionType.LOCALITY},
    DivisionLevel.SUBLOCALITY_LEVEL_1: {DivisionType.CITY_DISTRICT},
}
HIERARCHY_LEVELS = {
    1: DivisionLevel.ADMINISTRATIVE_LEVEL_1,
    2: DivisionLevel.ADMINISTRATIVE_LEVEL_2,
    3: DivisionLevel.ADMINISTRATIVE_LEVEL_3,
    4: DivisionLevel.LOCALITY,
}
CODE_TYPES = {
    # міста обласного значення
    (3, 1): {DivisionType.LOCALITY},
    # райони Автономної Республіки Крим, області
    (3, 2): {DivisionType.REGION},
    # райони міст, що мають спеціальний статус
    (3, 3): {DivisionType.CITY_DISTRICT},

    # міста районного значення
    (6, 1): {DivisionType.LOCALITY, DivisionType.CITY},
    # is unused
    (6, 2): set(),
    # райони в містах обласного значення
    (6, 3): {DivisionType.CITY_DISTRICT},
    # селища міського типу, що входять до складу міськради
    (6, 4): {DivisionType.LOCALITY, DivisionType.TOWN},
    # селища міського типу, що входять до складу райради
    (6, 5): {DivisionType.LOCALITY, DivisionType.TOWN},
    # селища міського типу, що входять до складу райради в місті
    (6, 6): {DivisionType.LOCALITY, DivisionType.TOWN},
    # міста, що входять до складу міськради
    (6, 7): {DivisionType.LOCALITY, DivisionType.CITY},
    # сільради, що входять до складу райради
    (6, 8): {DivisionType.COMMUNE},
    # сільради, села, що входять до складу райради міста, міськради
    (6, 9): {DivisionType.COMMUNE},
}
TYPE_LEVELS = {
    DivisionType.CITY: DivisionLevel.LOCALITY,
    DivisionType.REGION: DivisionLevel.ADMINISTRATIVE_LEVEL_1,
    DivisionType.CITY_DISTRICT: DivisionLevel.SUBLOCALITY_LEVEL_1,
    DivisionType.MUNICIPALITY: DivisionLevel.ADMINISTRATIVE_LEVEL_2,
    DivisionType.DISTRICT: DivisionLevel.ADMINISTRATIVE_LEVEL_2,
    DivisionType.COMMUNE: DivisionLevel.ADMINISTRATIVE_LEVEL_3,
    DivisionType.COMMUNITY: DivisionLevel.ADMINISTRATIVE_LEVEL_3,
    DivisionType.TOWN: DivisionLevel.LOCALITY,
    DivisionType.LOCALITY: DivisionLevel.LOCALITY,
    DivisionType.VILLAGE: DivisionLevel.LOCALITY,
    DivisionType.HAMLET: DivisionLevel.LOCALITY,
}


def get_code_types(code: str) -> Set[DivisionType]:
    chars = [(char, code[char-1]) for char in (2, 6)]
    types = set()

    for code_type in chars:
        if code_type not in CODE_TYPES:
            continue

        types |= CODE_TYPES[code_type]

    return types


def get_category_types(category: Category) -> Set[DivisionType]:
    return CATEGORY_TYPES.get(category) or set()


def get_level_types(level: DivisionLevel) -> Set[DivisionType]:
    return LEVELS_TYPES.get(level) or set()


def get_category_level(category: Category) -> DivisionLevel:
    return CATEGORY_LEVELS.get(category, None)


def get_hierarchy_level(hierarchy: int) -> DivisionLevel:
    return HIERARCHY_LEVELS.get(hierarchy, None)


def get_type_levels(types: Set[DivisionType]) -> Set[DivisionLevel]:
    return {TYPE_LEVELS[t] for t in types if t in TYPE_LEVELS}
