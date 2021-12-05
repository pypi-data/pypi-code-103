#!/usr/bin/env python3

"""
** Allows to serialize and deserialize small objects native to python. **
-------------------------------------------------------------------------

Each function is specialized in only 1 type of objects.
The functions are called automatically according to the name of the classes of the objects.
That's why functions must end with the exact name of the class they deal with.
"""

import struct
import sys

from raisin.serialization.constants import HEADER


def serialize_float(obj, compact, **_):
    r"""
    ** Serialize the floats. **

    Examples
    --------
    >>> from raisin.serialization.atoms_builtins import serialize_float
    >>> b''.join(serialize_float(.0, compact=False))
    b'</>float</>0.0'
    >>> b''.join(serialize_float(.0, compact=True))
    b'\x06\x9c'
    >>> b''.join(serialize_float(2e16, compact=False))
    b'</>float</>2e+16'
    >>>
    """
    if compact:
        as_str = str(obj)
        if as_str.startswith('0.'): # 0.123 -> .123
            as_str = as_str[1:]
        elif as_str.startswith('-0.'): # -0.123 -> -.123
            as_str = as_str[0] + as_str[2:]
        elif as_str.endswith('.0'): # 12.0 -> 12
            as_str = as_str[:-2]
            end_0 = 0 # nbr of 0 at end
            while as_str[-end_0-1:] == '0'*(end_0+1):
                end_0 += 1
            if end_0 >= 3:
                as_str = as_str[:-end_0] + 'e' + str(end_0)
        as_str = as_str.replace('e+', 'e')

        if len(as_str) < 16:
            if len(as_str) % 2:
                as_str = '0' + as_str
            pack = b''
            cor = {**{str(i): i for i in range(10)}, **{'-': 10, 'e': 11, '.': 12}}
            for i in range(0, len(as_str), 2):
                pack += bytes([cor[as_str[i+1]] + cor[as_str[i]]*len(cor)])
            yield HEADER['round_float'][1] + pack
        else:
            yield HEADER['normal_float'][1] + struct.pack('d', obj)
    else:
        yield HEADER['float'][0] + str(obj).encode()

def serialize_int(obj, compact, **_):
    r"""
    ** Serialize the integers. **

    Examples
    --------
    >>> from raisin.serialization.atoms_builtins import serialize_int
    >>> b''.join(serialize_int(0, compact=False))
    b'</>small int</>0'
    >>> b''.join(serialize_int(0, compact=True))
    b'\x03\x00'
    >>> b''.join(serialize_int(3**190, compact=False))
    b'</>large int</>#T\xd0i\\\x88\x00\xeeY\xe26\xb2{\xafm\x7f\xab\x99\x1e\x82]\xf0n.\x80@\xe344\x86\xae\xfe\xb4!{\x90\xcd9'
    >>>
    """
    if not compact and sys.getsizeof(obj) <= 64:
        yield HEADER['small_int'][0] + str(obj).encode()
    else:
        yield HEADER['large_int'][compact] + obj.to_bytes(
            length=(8 + (obj + (obj < 0)).bit_length()) // 8,
            byteorder='big',
            signed=True)

def serialize_NoneType(compact, **_):
    r"""
    ** Serialize the NoneType. **

    Examples
    --------
    >>> from raisin.serialization.atoms_builtins import serialize_NoneType
    >>> b''.join(serialize_NoneType(False))
    b'</>none</>'
    >>> b''.join(serialize_NoneType(True))
    b'\x13'
    >>>
    """
    yield HEADER['null'][compact]
