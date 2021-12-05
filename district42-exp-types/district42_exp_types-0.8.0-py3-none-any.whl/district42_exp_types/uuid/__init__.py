from district42 import register_type

from ._uuid_generator import UUIDGenerator
from ._uuid_representor import UUIDRepresentor
from ._uuid_schema import UUIDProps, UUIDSchema
from ._uuid_substitutor import UUIDSubstitutor
from ._uuid_validator import UUIDValidator

schema_uuid = register_type("uuid", UUIDSchema)

__all__ = ("UUIDSchema", "UUIDProps", "schema_uuid",
           "UUIDGenerator", "UUIDRepresentor", "UUIDSubstitutor", "UUIDValidator",)
