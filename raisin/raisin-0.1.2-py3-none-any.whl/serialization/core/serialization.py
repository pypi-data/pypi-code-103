#!/usr/bin/env python3

"""
** core of serialization. **
----------------------------

Here, the fundamental functions of serialization are written.
This is where the basic functions are coded.
"""

import os
import struct
import sys

from raisin.serialization.constants import HEADER


def main_serialize(obj, *, compresslevel, copy_file, psw, authenticity, parallelization_rate):
    """
    ** Allows you to add cryptographic and compression post-processes. **

    This function considers that the inputs are corect.
    There is no verification done on the inputs.
    In case your program controls the inputs, you should use this function.
    Otherwise, use the ``raisin.serialization.serialize`` function.
    """
    kind = obj.__class__.__name__
    if kind in FONC_TABLE:
        ser_obj = FONC_TABLE[kind](obj, bool(copy_file))
    else:
        raise NotImplementedError(f'{kind} objects are not supported')

    # compression and encryption
    if compresslevel > 1:
        raise NotImplementedError('pas possible de compresser pour le moment')
    if authenticity:
        raise NotImplementedError('pas de hash dispo')
    if psw is not None:
        raise NotImplementedError('pas de chiffrage')
    yield from ser_obj

def is_jsonisable(obj, copy_file):
    """
    ** Checks if the object can be serialized with json. **

    Examples
    --------
    >>> from raisin.serialization.core.serialization import is_jsonisable
    >>> copy_file = True
    >>> is_jsonisable(0, copy_file)
    True
    >>> is_jsonisable(.0, copy_file)
    True
    >>> is_jsonisable(True, copy_file)
    True
    >>> is_jsonisable(None, copy_file)
    True
    >>> is_jsonisable('a string', copy_file)
    True
    >>> is_jsonisable(b'a bytes', copy_file)
    False
    >>> is_jsonisable(('a tuple',), copy_file)
    False
    >>> is_jsonisable([1, 2, 3], copy_file)
    True
    >>> is_jsonisable([1, b'', 3], copy_file)
    False
    >>> is_jsonisable({1: 'a'}, copy_file)
    True
    >>> is_jsonisable({1: b'a'}, copy_file)
    False
    >>>
    """
    kind = obj.__class__.__name__
    if kind in {'int', 'float', 'bool', 'NoneType'}:
        return True
    if kind == 'str' and ((not copy_file) or (len(obj)<32767 and not os.path.isfile(obj))):
        return True
    if kind == 'list':
        return all(is_jsonisable(elem, copy_file) for elem in obj)
    if kind == 'dict':
        return all(is_jsonisable(key, copy_file) and is_jsonisable(value, copy_file)
                   for key, value in obj.items())
    return False

def _ser_float(obj, compact):
    r"""
    ** Serialize the floats. **

    Examples
    --------
    >>> from raisin.serialization.core.serialization import _ser_float
    >>> b''.join(_ser_float(.0, compact=False))
    b'</>float</>0.0'
    >>> b''.join(_ser_float(.0, compact=True))
    b'\x06\x9c'
    >>> b''.join(_ser_float(2e16, compact=False))
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
            yield HEADER['round float'][1] + pack
        else:
            yield HEADER['normal float'][1] + struct.pack('d', obj)
    else:
        yield HEADER['float'][0] + str(obj).encode()

def _ser_int(obj, compact):
    r"""
    ** Serialize the integers. **

    Examples
    --------
    >>> from raisin.serialization.core.serialization import _ser_int
    >>> b''.join(_ser_int(0, compact=False))
    b'</>small int</>0'
    >>> b''.join(_ser_int(0, compact=True))
    b'\x03\x00'
    >>> b''.join(_ser_int(3**190, compact=False))
    b'</>large int</>#T\xd0i\\\x88\x00\xeeY\xe26\xb2{\xafm\x7f\xab\x99\x1e\x82]\xf0n.\x80@\xe344\x86\xae\xfe\xb4!{\x90\xcd9'
    >>>
    """
    if not compact and sys.getsizeof(obj) <= 64:
        yield HEADER['small int'][0] + str(obj).encode()
    else:
        yield HEADER['large int'][compact] + obj.to_bytes(
            length=(8 + (obj + (obj < 0)).bit_length()) // 8,
            byteorder='big',
            signed=True)

def _ser_null(_, compact):
    r"""
    ** Serialize the NoneType. **

    Examples
    --------
    >>> from raisin.serialization.core.serialization import _ser_null
    >>> b''.join(_ser_null(None, False))
    b'</>none</>'
    >>> b''.join(_ser_null(None, True))
    b'\x13'
    >>>
    """
    yield HEADER['null'][compact]

FONC_TABLE = {
    'float': _ser_float,
    'int': _ser_int,
    'NoneType': _ser_null,
}
