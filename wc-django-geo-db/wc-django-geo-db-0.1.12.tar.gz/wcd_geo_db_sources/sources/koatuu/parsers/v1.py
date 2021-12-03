import json
from typing import Dict, Set, TYPE_CHECKING, TextIO, List
from enum import Enum
import tempfile

from ..code_seeker import KOATUU_SEEKER
from .shared import (
    json_encoder,
    Geo, order_geos, update_geo,
    get_category,
    collect_hierarchy, postprocess_items,
)

if TYPE_CHECKING:
    from ..process import KOATUUImportRunner


Hierarchy = Dict[str, Set[str]]


class Field(str, Enum):
    LEVEL_1: str = 'Перший рівень'
    LEVEL_2: str = 'Другий рівень'
    LEVEL_3: str = 'Третій рівень'
    LEVEL_4: str = 'Четвертий рівень'
    CATEGORY: str = 'Категорія'
    TITLE: str = 'Назва об\'єкта українською мовою'


def get_path(raw: dict) -> List[str]:
    levels = [
        str(raw.get(x, '')) or None
        for x in (Field.LEVEL_1, Field.LEVEL_2, Field.LEVEL_3, Field.LEVEL_4)
    ]
    index, id = next(x for x in enumerate(reversed(levels)) if x[1] is not None)

    return levels[:len(levels) - index]


def create_geo(raw: dict) -> Geo:
    path = [(KOATUU_SEEKER.name, code) for code in get_path(raw)]

    return update_geo(Geo(
        code=path[-1],
        path=path[:-1],
        name=raw.get(Field.TITLE) or None,
        category=get_category(raw.get(Field.CATEGORY) or None),
    ))


def parse(data: List[dict]) -> List[Geo]:
    items = order_geos(map(create_geo, data))
    items = postprocess_items(items, collect_hierarchy(items))

    return items


def run_parser(runner: 'KOATUUImportRunner', file: TextIO):
    items = parse(json.loads(file.read()))

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write(json.dumps(
            items,
            default=json_encoder
        ))

    return tmp.name
