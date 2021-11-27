from cffi import FFI
ffibuilder = FFI()

ffibuilder.cdef("""
    void tmu_encode(unsigned int *X, unsigned int *encoded_X, int number_of_examples, int dim_x, int dim_y, int dim_z, int patch_dim_x, int patch_dim_y, int append_negated, int class_features);
    """)

ffibuilder.set_source("tmu._tools",  # name of the output C extension
"""
    #include "./tmu/Tools.h"
""",
    include_dirs=['.'],
    sources=['./tmu/Tools.c'],   
    libraries=['m'])

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
