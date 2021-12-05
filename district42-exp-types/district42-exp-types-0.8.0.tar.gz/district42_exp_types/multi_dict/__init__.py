from district42 import register_type

from ._multi_dict_generator import MultiDictGenerator
from ._multi_dict_representor import MultiDictRepresentor
from ._multi_dict_schema import MultiDictProps, MultiDictSchema
from ._multi_dict_substitutor import MultiDictSubstitutor, MultiDictSubstitutorValidator
from ._multi_dict_validator import MultiDictValidator

schema_multi_dict = register_type("multi_dict", MultiDictSchema)

__all__ = ("schema_multi_dict", "MultiDictSchema", "MultiDictProps", "MultiDictRepresentor",
           "MultiDictValidator", "MultiDictSubstitutor", "MultiDictGenerator",
           "MultiDictSubstitutorValidator",)
