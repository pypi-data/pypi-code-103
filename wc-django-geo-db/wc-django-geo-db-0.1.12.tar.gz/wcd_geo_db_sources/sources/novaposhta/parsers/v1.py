import json
from decimal import Decimal
from typing import Dict, Set, TYPE_CHECKING, TextIO, List
from enum import Enum
import tempfile

from wcd_geo_db_sources.sources.koatuu.code_seeker import KOATUU_SEEKER
from ..code_seeker import NOVAPOSHTA_SEEKER
from ..const import UKRAINIAN_LANGUAGE, RUSSIAN_LANGUAGE
from .shared import (
    json_encoder,
    Geo, update_geo,
)

if TYPE_CHECKING:
    from ..process import NOVAPOSHTAImportRunner


def normalize_koatuu(value: str) -> str:
    return ('000000000' + value)[-10:]


def create_geo(raw: dict) -> Geo:
    code = (NOVAPOSHTA_SEEKER.name, NOVAPOSHTA_SEEKER.to_value(
        NOVAPOSHTA_SEEKER.make(
            type=NOVAPOSHTA_SEEKER.Type.SETTLEMENT, ref=raw['Ref']
        )
    ))
    codes = [code]

    if raw['IndexCOATSU1']:
        codes.append((KOATUU_SEEKER.name, normalize_koatuu(raw['IndexCOATSU1'])))

    return update_geo(Geo(
        code=code, codes=codes, path=[],
        name=raw.get('Description') or None,
        point={
            'latitude': Decimal(raw.get('Latitude') or 0),
            'longitude': Decimal(raw.get('Longitude') or 0),
        } if 'Latitude' in raw and raw['Latitude'] else None,
        translations=[
            {'code': code, 'language': lang, 'name': name}
            for lang, name in (
                (UKRAINIAN_LANGUAGE, raw.get('Description')),
                (RUSSIAN_LANGUAGE, raw.get('DescriptionRu')),
            ) if name
        ]
    ))


def parse(data: List[dict]) -> List[Geo]:
    items = [create_geo(x) for x in data]

    return items


def run_parser(runner: 'NOVAPOSHTAImportRunner', file: TextIO):
    items = parse(json.loads(file.read()))

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write(json.dumps(items, default=json_encoder))

    return tmp.name
