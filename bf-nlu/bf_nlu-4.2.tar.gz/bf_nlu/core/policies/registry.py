# Import all policies at one place to be able to to resolve them via a common module
# path. Don't do this in `__init__.py` to avoid importing them without need.

# noinspection PyUnresolvedReferences
from bf_nlu.core.policies.ted_policy import TEDPolicy

# noinspection PyUnresolvedReferences
from bf_nlu.core.policies.embedding_policy import EmbeddingPolicy

# noinspection PyUnresolvedReferences
from bf_nlu.core.policies.fallback import FallbackPolicy

# noinspection PyUnresolvedReferences
from bf_nlu.core.policies.keras_policy import KerasPolicy

# noinspection PyUnresolvedReferences
from bf_nlu.core.policies.memoization import MemoizationPolicy, AugmentedMemoizationPolicy

# noinspection PyUnresolvedReferences
from bf_nlu.core.policies.sklearn_policy import SklearnPolicy

# noinspection PyUnresolvedReferences
from bf_nlu.core.policies.form_policy import FormPolicy

# noinspection PyUnresolvedReferences
from bf_nlu.core.policies.two_stage_fallback import TwoStageFallbackPolicy

# noinspection PyUnresolvedReferences
from bf_nlu.core.policies.mapping_policy import MappingPolicy

# noinspection PyUnresolvedReferences
from bf_nlu.core.policies.embedding_policy import EmbeddingPolicy
