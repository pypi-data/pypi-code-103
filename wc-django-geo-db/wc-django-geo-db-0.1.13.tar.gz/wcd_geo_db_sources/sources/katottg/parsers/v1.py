import json
from functools import reduce
from typing import Dict, Set, TYPE_CHECKING, TextIO, TypedDict, List, Optional
from enum import Enum
import tempfile
from pandas import read_excel
from numpy import nan

from wcd_geo_db.const import DivisionLevel, DivisionType

from wcd_geo_db_sources.modules.merger.dtos import DivisionItem
from ..._base.parser import json_encoder
from ..code_seeker import KATOTTG_SEEKER

if TYPE_CHECKING:
    from ..process import KATOTTGImportRunner


UA_CODE = 'UA'


class Field(int, Enum):
    LEVEL_1: int = 1
    LEVEL_2: int = 2
    LEVEL_3: int = 3
    LEVEL_4: int = 4
    LEVEL_5: int = 5
    CATEGORY: int = 6
    TITLE: int = 7


class Category(str, Enum):
    OBLAST = chr(79) # 'О'
    AUTONOMOUS_CITY = chr(75) # 'К'
    REGION = chr(80) # 'Р'
    HROMADA = chr(72) # 'Н'
    CITY = chr(77) # 'М'
    TOWN = chr(84) # 'Т'
    VILLAGE = chr(67) # 'С'
    HAMLET = chr(88) # 'Х'
    CITY_DISTRICT = chr(66) # 'В'


CATEGORY_TYPES = {
    Category.OBLAST: {DivisionType.REGION},
    Category.AUTONOMOUS_CITY: {DivisionType.AUTONOMOUS_CITY, DivisionType.CITY},
    Category.REGION: {DivisionType.DISTRICT, DivisionType.MUNICIPALITY},
    Category.HROMADA: {DivisionType.COMMUNE, DivisionType.COMMUNITY},
    Category.CITY: {DivisionType.LOCALITY, DivisionType.CITY},
    Category.TOWN: {DivisionType.LOCALITY, DivisionType.TOWN},
    Category.VILLAGE: {DivisionType.LOCALITY, DivisionType.VILLAGE},
    Category.HAMLET: {DivisionType.LOCALITY, DivisionType.HAMLET},
    Category.CITY_DISTRICT: {DivisionType.CITY_DISTRICT},
}
CATEGORY_ALIASES = {
    chr(1057): Category.VILLAGE,
}
CATEGORY_LEVELS = {
    Category.OBLAST: DivisionLevel.ADMINISTRATIVE_LEVEL_1,
    Category.AUTONOMOUS_CITY: DivisionLevel.LOCALITY,
    Category.REGION: DivisionLevel.ADMINISTRATIVE_LEVEL_2,
    Category.HROMADA: DivisionLevel.ADMINISTRATIVE_LEVEL_3,
    Category.CITY: DivisionLevel.LOCALITY,
    Category.TOWN: DivisionLevel.LOCALITY,
    Category.VILLAGE: DivisionLevel.LOCALITY,
    Category.HAMLET: DivisionLevel.LOCALITY,
    Category.CITY_DISTRICT: DivisionLevel.SUBLOCALITY_LEVEL_1,
}


class Geo(DivisionItem):
    category: Optional[Category]


def deduplicate_path(path: List[str]):
    seen = set()
    seen_add = seen.add

    return [x for x in path if not (x in seen or seen_add(x))]


def get_path(raw: list) -> List[str]:
    levels = [
        str('' if raw[x] is nan else raw[x]) or None
        for x in (Field.LEVEL_1, Field.LEVEL_2, Field.LEVEL_3, Field.LEVEL_4, Field.LEVEL_5)
    ]
    index, id = next(x for x in enumerate(reversed(levels)) if x[1] is not None)

    return deduplicate_path(levels[:len(levels) - index])


def get_category(c: str):
    if c in CATEGORY_ALIASES:
        c = CATEGORY_ALIASES[c]

    if c in Category._value2member_map_:
        return Category(c)

    raise Exception(f'{ord(c)} "{c}"')

    return None


def get_types(geo: Geo):
    category = geo['category']
    types = set()

    if category:
        types |= CATEGORY_TYPES[category]

    return types


def get_level(geo: Geo):
    level = None
    category = geo['category']

    if category is not None:
        level = CATEGORY_LEVELS.get(category, None)

    return level


def create_geo(raw: list) -> Geo:
    path = [(KATOTTG_SEEKER.name, code) for code in get_path(raw)]
    geo: Geo = Geo(
        code=path[-1],
        path=path[:-1],
        name=raw[Field.TITLE] or None,
        category=get_category(raw[Field.CATEGORY] or None),
    )
    geo['types'] = get_types(geo)
    geo['level'] = get_level(geo)

    return geo


def order_key(geo: Geo):
    return (len(geo['path']), geo['code'])


def parse(runner: 'KATOTTGImportRunner', file: TextIO):
    dfs = read_excel(file.name)
    simplified_data = (
        [value for value in row]
        for row in dfs.itertuples()
        if (
            row[Field.LEVEL_1] and
            isinstance(row[Field.LEVEL_1], str) and
            row[Field.LEVEL_1].startswith(UA_CODE)
        )
    )

    items = list(sorted(map(create_geo, simplified_data), key=order_key))

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write(json.dumps(
            items,
            default=json_encoder
        ))

    return tmp.name
