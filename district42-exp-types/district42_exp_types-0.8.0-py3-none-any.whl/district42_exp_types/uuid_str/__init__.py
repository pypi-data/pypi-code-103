from district42 import register_type

from ._uuid_str_generator import UUIDStrGenerator
from ._uuid_str_representor import UUIDStrRepresentor
from ._uuid_str_schema import UUIDStrProps, UUIDStrSchema
from ._uuid_str_substitutor import UUIDStrSubstitutor
from ._uuid_str_validator import StrCaseFormatter, StrCaseValidationError, UUIDStrValidator

schema_uuid_str = register_type("uuid_str", UUIDStrSchema)

__all__ = ("UUIDStrSchema", "UUIDStrProps", "schema_uuid_str",
           "UUIDStrGenerator", "UUIDStrRepresentor", "UUIDStrSubstitutor", "UUIDStrValidator",
           "StrCaseValidationError", "StrCaseFormatter",)
