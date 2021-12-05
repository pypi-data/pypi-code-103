from district42 import register_type

from ._numeric_generator import NumericGenerator
from ._numeric_representor import NumericRepresentor
from ._numeric_schema import NumericProps, NumericSchema
from ._numeric_substitutor import NumericSubstitutor
from ._numeric_validator import NumericValidator

schema_numeric = register_type("numeric", NumericSchema)

__all__ = ("NumericSchema", "NumericProps", "schema_numeric",
           "NumericGenerator", "NumericRepresentor", "NumericSubstitutor", "NumericValidator",)
