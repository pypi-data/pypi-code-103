import os
from cffi import FFI

__dir__ = os.path.dirname(os.path.abspath(__file__))

lib = os.path.join(__dir__, "lib")
lrt = [os.path.join(lib, "lib.so")]
header = os.path.join(lib, "lib.h")

ffi = FFI()

ffi.set_source(
    '_runtime',
    '#include <lib.h>',
    include_dirs=[lib],
    extra_objects=lrt,
)

with open(header, 'r') as f:
    ffi.cdef(f.read())


if __name__ == '__main__':
    ffi.compile()
