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
    >>> from raisin.serialization.atoms.small import serialize_float
    >>> b''.join(serialize_float(.0, compact=False))
    b'/float/0.0'
    >>> b''.join(serialize_float(.0, compact=True))
    b'\x06\xa8'
    >>> b''.join(serialize_float(2e16, compact=False))
    b'/float/2e+16'
    >>> b''.join(serialize_float(1.23456, compact=True))
    b'\x06\xb7\xaa.L'
    >>> b''.join(serialize_float(1.23456789123456, compact=True))
    b'\x07\xb7\xb4\xd8B\xca\xc0\xf3?'
    >>>
    """
    if compact:
        as_str = str(obj)
        if as_str.startswith('0.'):  # 0.123 -> .123
            as_str = as_str[1:]
        elif as_str.startswith('-0.'):  # -0.123 -> -.123
            as_str = as_str[0] + as_str[2:]
        elif as_str.endswith('.0'):  # 12.0 -> 12
            as_str = as_str[:-2]
            end_0 = 0  # nbr of 0 at end
            while as_str[-end_0 - 1 :] == '0' * (end_0 + 1):
                end_0 += 1
            if end_0 >= 3:
                as_str = as_str[:-end_0] + 'e' + str(end_0)
        as_str = as_str.replace('e+', 'e')

        if len(as_str) < 16:
            if len(as_str) % 2:
                as_str = ' ' + as_str
            pack = b''
            cor = {
                '0': 0,
                '1': 1,
                '2': 2,
                '3': 3,
                '4': 4,
                '5': 5,
                '6': 6,
                '7': 7,
                '8': 8,
                '9': 9,
                '-': 10,
                'e': 11,
                '.': 12,
                ' ': 13,
            }
            for i in range(0, len(as_str), 2):
                pack += bytes([cor[as_str[i + 1]] + cor[as_str[i]] * 14])
            yield HEADER['round_float'][1] + pack
        else:
            yield HEADER['normal_float'][1] + struct.pack('d', obj)
    else:
        yield HEADER['float'][0] + str(obj).encode()


def deserialize_float(pack, gen, **_):
    """
    ** Deserialize non compact floats. **

    Examples
    --------
    >>> from raisin.serialization.atoms.small import deserialize_float
    >>> deserialize_float(pack=b'0.0', gen=[])
    0.0
    >>>
    """
    return float(pack + b''.join(gen))


def deserialize_round_float(pack, gen, **_):
    r"""
    ** Deserialize non compact floats. **

    Examples
    --------
    >>> from raisin.serialization.atoms.small import deserialize_round_float
    >>> deserialize_round_float(pack=b'\xa8', gen=[])
    0.0
    >>> deserialize_round_float(pack=b'\xb7\xaa.L', gen=[])
    1.23456
    >>>
    """
    cor = {
        0: '0',
        1: '1',
        2: '2',
        3: '3',
        4: '4',
        5: '5',
        6: '6',
        7: '7',
        8: '8',
        9: '9',
        10: '-',
        11: 'e',
        12: '.',
        13: ' ',
    }
    return float(''.join(cor[octet // 14] + cor[octet % 14] for octet in (pack + b''.join(gen))))


def deserialize_normal_float(pack, gen, **_):
    r"""
    ** Deserialize non compact floats. **

    Examples
    --------
    >>> from raisin.serialization.atoms.small import deserialize_normal_float
    >>> deserialize_normal_float(pack=b'\xb7\xb4\xd8B\xca\xc0\xf3?', gen=[])
    1.23456789123456
    >>>
    """
    return struct.unpack('d', pack + b''.join(gen))[0]


def serialize_int(obj, compact, **_):
    r"""
    ** Serialize the integers. **

    Examples
    --------
    >>> from raisin.serialization.atoms.small import serialize_int
    >>> b''.join(serialize_int(0, compact=False))
    b'/small int/0'
    >>> b''.join(serialize_int(0, compact=True))
    b'\x03\x00'
    >>> b''.join(serialize_int(3**190, compact=False))
    b'/large int/#T\xd0i\\\x88\x00\xeeY\xe26\xb2{\xafm\x7f\xab\x99\x1e\x82]\xf0n.\x80@\xe344\x86\xae\xfe\xb4!{\x90\xcd9'
    >>>
    """
    if not compact and sys.getsizeof(obj) <= 64:
        yield HEADER['small_int'][0] + str(obj).encode()
    else:
        yield HEADER['large_int'][compact] + obj.to_bytes(
            length=(8 + (obj + (obj < 0)).bit_length()) // 8, byteorder='big', signed=True
        )


def deserialize_small_int(pack, gen, **_):
    """
    ** Deserialize small integers. **

    Examples
    --------
    >>> from raisin.serialization.atoms.small import deserialize_small_int
    >>> deserialize_small_int(pack=b'0', gen=[])
    0
    >>>
    """
    return int(pack + b''.join(gen))


def deserialize_large_int(pack, gen, **_):
    r"""
    ** Deserialize large integers. **

    Examples
    --------
    >>> from raisin.serialization.atoms.small import deserialize_large_int
    >>> deserialize_large_int(pack=b'#T\xd0i\\\x88\x00\xeeY\xe26\xb2{\xafm\x7f\xab\x99\x1e\x82]\xf0'
    ...     b'n.\x80@\xe344\x86\xae\xfe\xb4!{\x90\xcd9', gen=[])
    4498196224760364601242719132174628305800834098010033971355568455673974002968757862019419449
    >>>
    """
    return int.from_bytes(pack + b''.join(gen), byteorder='big', signed=True)


def serialize_NoneType(compact, **_):
    r"""
    ** Serialize the NoneType. **

    Examples
    --------
    >>> from raisin.serialization.atoms.small import serialize_NoneType
    >>> b''.join(serialize_NoneType(False))
    b'/none/'
    >>> b''.join(serialize_NoneType(True))
    b'\x13'
    >>>
    """
    yield HEADER['null'][compact]


def deserialize_null(**_):
    """
    ** Deserialize None. **

    Examples
    --------
    >>> from raisin.serialization.atoms.small import deserialize_null
    >>> deserialize_null()
    >>>
    """
    return None
