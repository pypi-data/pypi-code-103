import os

_jax_enable_x64 = os.getenv("JAX_ENABLE_X64")
if _jax_enable_x64 is None or not ("true" in _jax_enable_x64.lower()):
    import jax

    jax.config.update("jax_enable_x64", True)
    del jax

del _jax_enable_x64
del os

from .array import (
    ndarray,
    array,
    asarray,
    to_jax,
    to_adjfloat,
    set_default_dtype,
    get_default_dtype,
)
from .jax import overload_jax
