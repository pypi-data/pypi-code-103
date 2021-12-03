import json
from typing import TYPE_CHECKING, TextIO
import tempfile

from .shared import json_encoder
from ..const import GENERAL_LANGUAGE

if TYPE_CHECKING:
    from ..process import DELIVERY_AUTOImportRunner


def map_by_id(langs: dict):
    map = {}

    for lang, items in langs.items():
        for item in items:
            map[item['id']] = map.get(item['id']) or {}
            map[item['id']][lang] = item

    return map


def collect_alternates(mapped: dict, key: str, alternates: dict = None):
    alternates = alternates or {}

    for id, translations in mapped.items():
        general = translations[GENERAL_LANGUAGE][key]
        alternates[general] = alternates.get(general) or {}

        for language, item in translations.items():
            alternates[general][language] = alternates[general].get(language) or set()
            alternates[general][language].add(item[key])

    return alternates


def parse(data):
    cities = map_by_id(data['cities'])
    regions = map_by_id(data['regions'])

    alternates = collect_alternates(cities, 'name', alternates={})
    alternates = collect_alternates(cities, 'districtName', alternates=alternates)
    alternates = collect_alternates(regions, 'name', alternates=alternates)

    return list(alternates.items())


def run_parser(runner: 'DELIVERY_AUTOImportRunner', file: TextIO):
    items = parse(json.loads(file.read()))

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write(json.dumps(items, default=json_encoder))

    return tmp.name
