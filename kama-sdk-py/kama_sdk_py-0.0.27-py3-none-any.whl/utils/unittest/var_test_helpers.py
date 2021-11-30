from kama_sdk.model.base.mc import KIND_KEY, ID_KEY
from kama_sdk.model.predicate.predicate import CHECK_AGAINST_KEY, CHALLENGE_KEY, Predicate
from kama_sdk.model.variable.manifest_variable import ManifestVariable
from kama_sdk.model.variable.manifest_variable_dependency import ManifestVariableDependency, TO_KEY, \
  FROM_KEY
from kama_sdk.model.variable.manifest_variable_dependency_instance import ACTIVE_CHECK_PRED_KEY, EFFECT_KEY, \
  EFFECT_PREVENTS_READ

variable_descriptors = [
  {
    KIND_KEY: ManifestVariable.__name__,
    ID_KEY: 'one.one'
  },
  {
    KIND_KEY: ManifestVariable.__name__,
    ID_KEY: 'one.two'
  },
  {
    KIND_KEY: ManifestVariable.__name__,
    ID_KEY: 'two.one'
  },
  {
    KIND_KEY: ManifestVariable.__name__,
    ID_KEY: 'two.two'
  }
]


dependency_descriptor = [
  {
    ID_KEY: 'dependency-one',
    KIND_KEY: ManifestVariableDependency.__name__,
    FROM_KEY: {ID_KEY: 'one.one'},
    TO_KEY: {ID_KEY: "two\\..+"},
    EFFECT_KEY: EFFECT_PREVENTS_READ,
    ACTIVE_CHECK_PRED_KEY: {
      KIND_KEY: Predicate.__name__,
      CHALLENGE_KEY: "get::self>>to_variable>>value",
      CHECK_AGAINST_KEY: "y"
    }
  }
]
