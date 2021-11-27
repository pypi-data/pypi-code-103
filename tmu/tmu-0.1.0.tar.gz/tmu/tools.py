from ._tools import ffi, lib

def encode(X, encoded_X, number_of_examples, dim_x, dim_y, dim_z, patch_dim_x, patch_dim_y, class_features):
	lib.tmu_encode(ffi.cast("unsigned int *", X.ctypes.data), ffi.cast("unsigned int *", encoded_X.ctypes.data), number_of_examples, dim_x, dim_y, dim_z, patch_dim_x, patch_dim_y, 1, class_features);