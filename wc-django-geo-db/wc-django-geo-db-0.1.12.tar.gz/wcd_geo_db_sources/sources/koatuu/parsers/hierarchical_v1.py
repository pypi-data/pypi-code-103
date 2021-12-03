import json
from typing import Dict, Sequence, Set, TYPE_CHECKING, TextIO, List, TypedDict
from enum import Enum
import tempfile

from ..code_seeker import KOATUU_SEEKER
from .shared import (
    json_encoder,
    Category, get_category,
    Geo, order_geos, update_geo,
    collect_hierarchy, postprocess_items,
)

if TYPE_CHECKING:
    from ..process import KOATUUImportRunner


Hierarchy = Dict[str, Set[str]]


class Raw(TypedDict):
    code: str
    name: str
    type: str
    level1: List['Raw']
    level2: List['Raw']
    level3: List['Raw']
    level4: List['Raw']


class Flattened(TypedDict):
    path: Sequence[str]
    name: str
    category: Category


def create_geo(item: Flattened) -> Geo:
    path = [(KOATUU_SEEKER.name, str(code)) for code in item['path']]

    return update_geo(Geo(
        code=path[-1],
        path=path[:-1],
        name=item['name'],
        category=item['category'],
    ))


CHILDREN_FIELDS = 'level1', 'level2', 'level3', 'level4', 'level5'


def get_children(item: Raw) -> List[Raw]:
    for field in CHILDREN_FIELDS:
        if field in item:
            return item[field] or []

    return []


def flatten_data(items: List[Raw], path: List[str]) -> List[Flattened]:
    result = []

    for item in items:
        flattened: Flattened = {
            'path': path + [str(item['code'])],
            'name': item.get('name'),
            'category': get_category(item.get('type'))
        }
        result.append(flattened)
        children = get_children(item)

        if len(children) > 0:
            result += flatten_data(children, flattened['path'])

    return result


def parse(data: dict) -> List[Geo]:
    data = flatten_data(get_children(data), [])
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
