import json
from typing import TypedDict
from wcd_geo_db.modules.code_seeker import CodeSeeker

from .const import SOURCE, Type


__all__ = (
    'DeliveryAutoCodeValue',
    'DeliveryAutoCodeSeeker',

    'DELIVERY_AUTO_SEEKER',
)


class DeliveryAutoCodeValue(TypedDict):
    type: str
    id: str


class DeliveryAutoCodeSeeker(CodeSeeker):
    Type = Type

    def to_representation(self, value: DeliveryAutoCodeValue) -> str:
        type, id = json.loads(value)

        return {'type': type, 'id': id}

    def to_value(self, representation: str) -> DeliveryAutoCodeValue:
        return json.dumps([representation['type'], representation['id']])

    def make(self, type: str, id: str) -> DeliveryAutoCodeValue:
        return {'type': type, 'id': id}


DELIVERY_AUTO_SEEKER = DeliveryAutoCodeSeeker(name=SOURCE)
