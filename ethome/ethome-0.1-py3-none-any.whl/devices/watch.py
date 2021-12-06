import struct
import numpy as np


_ONE_BYTE = ["c", "b", "B", "?"]
_TWO_BYTE = ["h", "H", "e"]
_FOUR_BYTE = ["i", "I", "l", "L", "f"]
_EIGHT_BYTE = ["q", "Q", "d"]


def UnpackData(bin_data, struct_formats="Qdddddddddd"):
    struct_len = 0
    for struct_format in struct_formats:
        if struct_format in _ONE_BYTE:
            struct_len += 1
        elif struct_format in _TWO_BYTE:
            struct_len += 2
        elif struct_format in _FOUR_BYTE:
            struct_len += 4
        elif struct_format in _EIGHT_BYTE:
            struct_len += 8
        else:
            pass

    unpack_len = len(bin_data) // struct_len
    unpacked_data = struct.unpack(struct_formats * unpack_len, bin_data)
    return np.asanyarray(unpacked_data).reshape((unpack_len, -1))

