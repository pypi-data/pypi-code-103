from district42 import register_type

from ._rollout import rollout
from ._sdict_generator import SDictGenerator
from ._sdict_representor import SDictRepresentor
from ._sdict_schema import SDictSchema
from ._sdict_substitutor import SDictSubstitutor
from ._sdict_validator import SDictValidator

schema_sdict = register_type("sdict", SDictSchema)

__all__ = ("SDictSchema", "schema_sdict", "SDictGenerator", "SDictRepresentor",
           "SDictSubstitutor", "SDictValidator", "rollout",)
