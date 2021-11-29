import bf_nlu.core
import sys
import warnings

# this makes sure old code can still import from `bf_nlu_core`
# although the package has been moved to `bf_nlu.core`
sys.modules["bf_nlu_core"] = bf_nlu.core

warnings.warn(
    "The 'bf_nlu_core' package has been renamed. You should change "
    "your imports to use 'bf_nlu.core' instead.",
    UserWarning,
)
