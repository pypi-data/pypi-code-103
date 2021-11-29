from __future__ import annotations
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> #
#           < IN THE NAME OF GOD >           #
# ------------------------------------------ #
__AUTHOR__ = "ToorajJahangiri"
__EMAIL__ = "Toorajjahangiri@gmail.com"
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< #

"""
Nested Cipher b64:
    B64 Base on 'BASE64 URLSAFE' Standard Library Python 3.9

    THIS IS NO CRYPTING DATA

    All Cipher Method Input Types 'Bytes' and Return 'Bytes'
    Encode Get 'BYTES'  Return 'URLSAFE BASE 64'
    Decode Get 'Encoded Data' Return 'SOURCE DATA'
"""

# IMPORTS
from base64 import urlsafe_b64encode, urlsafe_b64decode
from functools import lru_cache


__all__ = (
    'METHODS_NAMES',
    'b64_encode',
    'b64_decode',
    'ab64_encode',
    'ab64_decode',
    'mb64_encode',
    'mb64_decode',
    'eb64_encode',
    'eb64_decode',
    'lb64_encode',
    'lb64_decode',
    'rb64_encode',
    'rb64_decode',
    'rab64_encode',
    'rab64_decode',
    'rmb64_encode',
    'rmb64_decode',
    'reb64_encode',
    'reb64_decode',
    'rlb64_encode',
    'rlb64_decode',
    )

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\^////////////////////////////// #

"""
Changed: 
    1 - fix bug `reb64` same with `rlb64` now bug is fixed.
    2 - add `lru cache` must be some faster for big file.
"""

def _hook_name() -> list[str]:
    names = []
    for method in __all__:
        if method.endswith('encode'):
            names.append(method.split('_')[0])
        else:
            continue
    return names

# ALL NAMES
METHODS_NAMES = _hook_name()

# BASE 64 URL SAFE ENCODER
@lru_cache()
def b64_encode(data: bytes) -> bytes:
    """[Base64 urlsafe Standard Encoder]

    Args:
        data (bytes): [Input Data]

    Returns:
        bytes: [Base64 urlsafe Encoded data]
    """
    return urlsafe_b64encode(data)

# BASE 64 URL SAFE ENCODER
@lru_cache()
def b64_decode(data: str | bytes) -> bytes:
    """[Base64 urlsafe Standard Decoder]

    Args:
        data (str | bytes): [Input Base64 Encoded Data]

    Returns:
        bytes: [Decoded Data]
    """
    return urlsafe_b64decode(data)

# --- ~ --- #

# ALL BASE 64 ENCODER
def ab64_encode(data: bytes) -> bytes:
    """[All Base 64 Encode] one by one data coverting to base 64

    Args:
        data (bytes): [Input Data]

    Returns:
        bytes: [Urlsafe base 64]
    """
    data = b64_encode(data).decode()
    data = (b64_encode(i.encode('ascii')) for i in data)
    return b64_encode(b' '.join(iter(data)))

# ALL BASE 64 DECODER
def ab64_decode(data: bytes) -> bytes:
    """[All Base 64 Decode] one by one data coverting from base 64

    Args:
        data (bytes): [Input Data Base64 Urlsafe]

    Returns:
        bytes: [Source Data]
    """
    data = b64_decode(data).decode('ascii').split(' ')
    data = (b64_decode(i.encode('ascii')) for i in data)
    return b64_decode(b''.join(iter(data)))

# --- ~ --- #

# MID BASE 64 ENCODER
def mb64_encode(data: bytes) -> bytes:
    """[Mid Base 64 Encode] data coverting to ReSorting base 64

    Args:
        data (bytes): [Input Data]

    Returns:
        bytes: [Urlsafe base 64]
    """
    data = b64_encode(data).decode('ascii')
    mid = len(data) // 2
    data = data[mid :] + data[: mid]
    return b64_encode(data.encode('ascii'))

# MID BASE 64 DECODER
def mb64_decode(data: bytes) -> bytes:
    """[Mid Base 64 Decode] data coverting from ReSorting base 64

    Args:
        data (bytes): [Input Data Base64 Urlsafe]

    Returns:
        bytes: [Source Data]
    """
    data = b64_decode(data).decode('ascii')
    mid = len(data) // 2
    data = data[mid :] + data[: mid]
    return b64_decode(data.encode('ascii'))

# --- ~ --- #

# REVERSED BASE 64 ENCODER
def rb64_encode(data: bytes) -> bytes:
    """[Reverse Base 64 Encode] data coverting to Revering base 64

    Args:
        data (bytes): [Input Data]

    Returns:
        bytes: [Urlsafe base 64]
    """
    data = b64_encode(data).decode('ascii')
    data = b64_encode(''.join(reversed(data)).encode('ascii')).decode('ascii')
    return b64_encode(''.join(reversed(data)).encode('ascii'))

# REVERSED BASE 64 DECODER
def rb64_decode(data: bytes) -> bytes:
    """[Reverse Base 64 Encode] data coverting from Revering base 64

    Args:
        data (bytes): [Input Data Base64 Urlsafe]

    Returns:
        bytes: [Source Data]
    """
    data = b64_decode(data).decode('ascii')
    data = b64_decode(''.join(reversed(data)).encode('ascii')).decode('ascii')
    return b64_decode(''.join(reversed(data)).encode('ascii'))

# --- ~ --- #

# EXCLUSIVE BASE 64 ENCODER
def eb64_encode(data: bytes) -> bytes:
    """[Exclusive Base 64 Encode] data coverting to Exclusive base 64

    Args:
        data (bytes): [Input Data]

    Returns:
        bytes: [Urlsafe base 64]
    """
    data = ab64_encode(data).decode('ascii')
    data = (ab64_encode(i.encode('ascii')) for i in data)
    return mb64_encode(b' '.join(iter(data)))

# EXCLUSIVE BASE 64 DECODER
def eb64_decode(data: bytes) -> bytes:
    """[Exclusive Base 64 Encode] data coverting from Exclusive base 64

    Args:
        data (bytes): [Input Data Base64 Urlsafe]

    Returns:
        bytes: [Source Data]
    """
    data = mb64_decode(data).decode('ascii').split(' ')
    data = (ab64_decode(i.encode('ascii')) for i in data)
    return ab64_decode(b''.join(iter(data)))

# --- ~ --- #

# LONG BASE 64 ENCODER
def lb64_encode(data: bytes) -> bytes:
    """[Long Base 64 Encode] data coverting to Long base 64

    Args:
        data (bytes): [Input Data]

    Returns:
        bytes: [Urlsafe base 64]
    """
    data = mb64_encode(data).decode('ascii')
    data = (mb64_encode(i.encode('ascii')) for i in data)
    return mb64_encode(b' '.join(iter(data)))

# LONG BASE 64 DECODER
def lb64_decode(data: bytes) -> bytes:
    """[Long Base 64 Encode] data coverting from Long base 64

    Args:
        data (bytes): [Input Data Base64 Urlsafe]

    Returns:
        bytes: [Source Data]
    """
    data = mb64_decode(data).decode('ascii').split(' ')
    data = (mb64_decode(i.encode('ascii')) for i in data)
    return mb64_decode(b''.join(iter(data)))

# --- ~ --- #

# REVERSE ALL BASE 64 ENCODER
def rab64_encode(data: bytes) -> bytes:
    """[Reversed All Base 64 Encode] reversed one by one data coverting to base 64

    Args:
        data (bytes): [Input Data]

    Returns:
        bytes: [Urlsafe base 64]
    """
    return ab64_encode(rb64_encode(data))

# REVERSE ALL BASE 64 DECODER
def rab64_decode(data: bytes) -> bytes:
    """[Reversed All Base 64 Decode] reversed one by one data coverting from base 64

    Args:
        data (bytes): [Input Data Base64 Urlsafe]

    Returns:
        bytes: [Source Data]
    """
    return rb64_decode(ab64_decode(data))

# --- ~ --- #

# REVERSE MID BASE 64 ENCODER
def rmb64_encode(data: bytes) -> bytes:
    """[Reversed Mid Base 64 Encode] data coverting to Reversed Mid base 64

    Args:
        data (bytes): [Input Data]

    Returns:
        bytes: [Urlsafe base 64]
    """
    return mb64_encode(rb64_encode(data))

# REVERSE MID BASE 64 DECODER
def rmb64_decode(data: bytes) -> bytes:
    """[Reversed Mid Base 64 Encode] data coverting from Reversed Mid base 64

    Args:
        data (bytes): [Input Data Base64 Urlsafe]

    Returns:
        bytes: [Source Data]
    """
    return rb64_decode(mb64_decode(data))

# --- ~ --- #

# REVERSE EXCLUSIVE BASE 64 ENCODER
def reb64_encode(data: bytes) -> bytes:
    """[Reversed Exclusive Base 64 Encode] data coverting to Reversed Exclusive base 64

    Args:
        data (bytes): [Input Data]

    Returns:
        bytes: [Urlsafe base 64]
    """
    return eb64_encode(rb64_encode(data))

# REVERSE EXCLUSIVE BASE 64 DECODER
def reb64_decode(data: bytes) -> bytes:
    """[Reversed Exclusive Base 64 Encode] data coverting from Reversed Exclusive base 64

    Args:
        data (bytes): [Input Data Base64 Urlsafe]

    Returns:
        bytes: [Source Data]
    """
    return rb64_decode(eb64_decode(data))

# --- ~ --- #

# REVERSE LONG BASE 64 ENCODER
def rlb64_encode(data: bytes) -> bytes:
    """[Reversed Long Base 64 Encode] data coverting to Reversed Long base 64

    Args:
        data (bytes): [Input Data]

    Returns:
        bytes: [Urlsafe base 64]
    """
    return eb64_encode(lb64_encode(data))

# REVERSE LONG BASE 64 DECODER
def rlb64_decode(data: bytes) -> bytes:
    """[Reversed Long Base 64 Encode] data coverting from Reversed Long base 64

    Args:
        data (bytes): [Input Data Base64 Urlsafe]

    Returns:
        bytes: [Source Data]
    """
    return lb64_decode(eb64_decode(data))

__dir__ = (
    'METHODS_NAMES',
    'b64_encode',
    'b64_decode',
    'ab64_encode',
    'ab64_decode',
    'mb64_encode',
    'mb64_decode',
    'eb64_encode',
    'eb64_decode',
    'lb64_encode',
    'lb64_decode',
    'rb64_encode',
    'rb64_decode',
    'rab64_encode',
    'rab64_decode',
    'rmb64_encode',
    'rmb64_decode',
    'reb64_encode',
    'reb64_decode',
    'rlb64_encode',
    'rlb64_decode',
    )
