# auto-generated file
__all__ = ['lib', 'ffi']

import os
from crypto_crawler._lowlevel__ffi import ffi

lib = ffi.dlopen(os.path.join(os.path.dirname(__file__), '_lowlevel__lib.so'), 4098)
del os
