from district42 import register_type

from ._ci_multi_dict_generator import CIMultiDictGenerator
from ._ci_multi_dict_representor import CIMultiDictRepresentor
from ._ci_multi_dict_schema import CIMultiDictProps, CIMultiDictSchema
from ._ci_multi_dict_substitutor import CIMultiDictSubstitutor
from ._ci_multi_dict_validator import CIMultiDictValidator

schema_ci_multi_dict = register_type("ci_multi_dict", CIMultiDictSchema)

__all__ = ("schema_ci_multi_dict", "CIMultiDictSchema", "CIMultiDictProps",
           "CIMultiDictRepresentor", "CIMultiDictGenerator", "CIMultiDictSubstitutor",
           "CIMultiDictValidator",)
