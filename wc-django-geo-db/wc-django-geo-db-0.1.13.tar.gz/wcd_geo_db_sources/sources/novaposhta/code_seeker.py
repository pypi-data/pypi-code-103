import json
from typing import TypedDict
from wcd_geo_db.modules.code_seeker import CodeSeeker

from .const import SOURCE, Type


__all__ = (
    'NovaPoshtaCodeValue',
    'NovaPoshtaCodeSeeker',

    'NOVAPOSHTA_SEEKER',
)


class NovaPoshtaCodeValue(TypedDict):
    type: str
    ref: str


class NovaPoshtaCodeSeeker(CodeSeeker):
    Type = Type

    def to_representation(self, value: NovaPoshtaCodeValue) -> str:
        type, ref = json.loads(value)

        return {'type': type, 'ref': ref}

    def to_value(self, representation: str) -> NovaPoshtaCodeValue:
        return json.dumps([representation['type'], representation['ref']])

    def make(self, type: str, ref: str) -> NovaPoshtaCodeValue:
        return {'type': type, 'ref': ref}


NOVAPOSHTA_SEEKER = NovaPoshtaCodeSeeker(name=SOURCE)
