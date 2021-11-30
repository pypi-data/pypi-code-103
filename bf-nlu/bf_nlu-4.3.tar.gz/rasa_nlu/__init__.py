import bf_nlu.nlu
import sys
import warnings

# this makes sure old code can still import from `bf_nlu`
# although the package has been moved to `bf_nlu.nlu`
sys.modules["bf_nlu"] = bf_nlu.nlu

warnings.warn(
    "The 'bf_nlu_nlu' package has been renamed. You should change "
    "your imports to use 'bf_nlu.nlu' instead.",
    UserWarning,
)
