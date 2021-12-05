#!/usr/bin/env python3

"""
** core of serialization and deserialization. **
------------------------------------------------

This is the entry point for the function that manages
the analysis of objects and serialized chains.
This is where the link is made between the single-object
serialization/deserialization functions and the global serialization
management which is able to manage different types of objects.
"""

import os

from raisin.serialization.constants import (
    ALPHABET,
    ALPHABET2INDEX,
    BUFFER_SIZE,
    BYTES2HEADER,
    HEADERLEN,
    N_BYTES,
    N_SYMB,
)
from raisin.serialization.iter_tools import anticipate, to_gen
from raisin.serialization.atoms import SERIALIZE_TABLE, DESERIALIZE_TABLE


def serialize(obj, *, compresslevel, copy_file, psw, authenticity, paralleling_rate):
    """
    ** Allows to add cryptographic and compression post-processes. **

    Parameters
    ----------
    They are detailed in ``raisin.serialization.serialize``.

    Yields
    ------
        Packets of bytes of maximum size equal to *BUFFER_SIZE*.

    Notes
    -----
    This function considers that the inputs are corect.
    There is no verification done on the inputs.
    In case your program controls the inputs, you should use this function.
    Otherwise, use the ``raisin.serialization.serialize`` function.
    """
    kind = obj.__class__.__name__
    if kind in SERIALIZE_TABLE:
        ser_obj = SERIALIZE_TABLE[kind](
            obj=obj,
            compact=bool(compresslevel),
            copy_file=copy_file,
            paralleling_rate=paralleling_rate,
        )
    else:
        raise TypeError(f'Object of type {kind} is not raisin serializable.')

    # compression and encryption
    if compresslevel > 1:
        raise NotImplementedError('pas possible de compresser pour le moment')
    if authenticity:
        raise NotImplementedError('pas de hash dispo')
    if psw is not None:
        raise NotImplementedError('pas de chiffrage')
    yield from ser_obj


def deserialize(pack, gen, *, psw, paralleling_rate):
    """
    ** Allows to call the right functions to deserialize the data stream. **

    Parameters
    ----------
    pack : bytes
        The first part of the serialized object.
    gen : generator
        The continuation of the serialized object in the form of a byte string generator.

    Returns
    -------
    object
        The deserialized object.

    Other Parameters
    ----------------
    They are detailed in ``raisin.serialization.deserialize``.

    Notes
    -----
    This function considers that the inputs are corect.
    There is no verification done on the inputs.
    In case your program controls the inputs, you should use this function.
    Otherwise, use the ``raisin.serialization.deserialize`` function.
    The normalization of the inputs is done with ``raisin.serialization.iter_tools.to_gen``.
    """
    head, pack, gen = get_header(pack=pack, gen=gen)
    if head in DESERIALIZE_TABLE:
        return DESERIALIZE_TABLE[head](
            pack=pack, gen=gen, psw=psw, paralleling_rate=paralleling_rate
        )
    raise NotImplementedError(f'deserialization of {head} is not implemented.')


def bytes2str(gen):
    r"""
    ** Convert a batch of bytes to an ascii string. **

    Does not make any verifications on the inputs.
    Groups *N_BYTES* bytes in *N_SYMB* characters or *3* bytes in *4*
    characters depending on what allows to compact the result.
    Bijection of the ``str2bytes`` function.

    Parameters
    ----------
    gen : generator
        Generator coming directly from ``raisin.serialization.serialize``.
        It must not be empty or exhausted.
        Bijection of the ``str2bytes`` function.

    Returns
    -------
    str
        A printable ascii character string that allows to reconstitute the byte string.

    Notes
    -----
    adds a byte in the header that allows to know if the grouping is by small or large packets.

    Examples
    --------
    >>> from raisin.serialization.core import bytes2str
    >>> bytes2str([b'toto'])
    '0Dg90aabVb'
    >>> bytes2str([b'\x00'*10]*4)
    '1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaO'
    >>>
    """

    def int2str(nbr, n_symb, n_car):
        """
        ** Convert an integer to a string. **

        nbr <= n_car**n_symb

        Parameters
        ----------
        nbr : int
            The integer to be converted.
        n_symb : int
            The size of the output message.
        n_car : int
            The size of the alphabet to consider

        Returns
        -------
        str
            A string containing *n_symb* characters chosen
            from the alphabet *ALPHABET*.
        """
        string = ''
        while nbr:
            nbr, rest = divmod(nbr, n_car)
            string = ALPHABET[rest] + string
        string = ALPHABET[0] * (n_symb - len(string)) + string
        return string

    # preparation (n_car**n_symb >= n2**n_bytes)
    pack = b''.join(gen)
    if len(pack) < N_BYTES * 3 / 4:
        out = '0'
        n_car = 64
        n_bytes = 3
        n_symb = 4
    else:
        out = '1'
        n_car = len(ALPHABET)
        n_bytes = N_BYTES
        n_symb = N_SYMB

    # convertion
    for is_end, pack in anticipate(to_gen(pack=pack, size=n_bytes)):
        out += int2str(int.from_bytes(pack, byteorder='big', signed=False), n_symb, n_car)
        if is_end and len(pack) < n_bytes:
            return out + ALPHABET[len(pack)]
    return out


def str2bytes(string):
    """
    ** Convert an ascii string to a batch of bytes. **

    Does not make any verifications on the inputs.
    Bijection of the ``bytes2str`` function.

    Parameters
    ----------
    string : str
        A string from the str2bytes function.

    Returns
    -------
    bytes
        The bytes just before they are transformed into str.

    Raises
    ------
    ValueError
        If the header does not match.

    Examples
    --------
    >>> from raisin.serialization.core import str2bytes
    >>> str2bytes('0Dg90aabVb')
    b'toto'
    >>>
    """

    def alph_to_pack(phrases, n_car, n_bytes):
        """
        ** Convert a string tensor to a string of bytes. **
        """
        return b''.join(
            (
                sum(
                    ALPHABET2INDEX[symb] * n_car ** symb_po
                    for symb_po, symb in enumerate(reversed(phrase))
                ).to_bytes(n_bytes, byteorder='big', signed=False)
                for phrase in phrases
            )
        )

    # preparation (n_car**n_symb >= n2**n_bytes)
    head, string = string[0], string[1:]
    if head == '0':
        n_car = 64
        n_bytes = 3
        n_symb = 4
    elif head == '1':
        n_car = len(ALPHABET)
        n_bytes = N_BYTES
        n_symb = N_SYMB
    else:
        raise ValueError('The header can only be ' f"'0' or '1'. Not '{head}'.")

    # desencapsulation
    data = b''
    phrases = []
    bloc = BUFFER_SIZE // n_bytes
    for i, (is_end, phrase) in enumerate(anticipate(to_gen(pack=string, size=n_symb))):
        if is_end and len(phrase) < n_symb:
            data += alph_to_pack(phrases, n_car, n_bytes)
            data = (
                data[:-n_bytes]
                + data[
                    -sum(
                        ALPHABET2INDEX[symb] * n_car ** symb_pos
                        for symb_pos, symb in enumerate(reversed(phrase))
                    ) :
                ]
            )
            return data
        phrases.append(phrase)
        if not i % bloc:
            data += alph_to_pack(phrases, n_car, n_bytes)
            phrases = []
    data += alph_to_pack(phrases, n_car, n_bytes)
    return data


def is_jsonisable(obj, copy_file):
    """
    ** Checks if the object can be serialized with json. **

    Examples
    --------
    >>> from raisin.serialization.core import is_jsonisable
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
    if kind == 'str' and ((not copy_file) or (len(obj) < 32767 and not os.path.isfile(obj))):
        return True
    if kind == 'list':
        return all(is_jsonisable(elem, copy_file) for elem in obj)
    if kind == 'dict':
        return all(
            is_jsonisable(key, copy_file) and is_jsonisable(value, copy_file)
            for key, value in obj.items()
        )
    return False


def size2tag(size):
    r"""
    ** Creates a flag that allows to group *size* bytes. **

    Parameters
    ----------
    size : int
        The number that can be encoded in the flag. >= 0

    Returns
    -------
    bytes
        The flags of variable size according to the size
        of the message to encode.

    Notes
    -----
    Can be very useful to record the size of a frame and be able
    to reconstruct it using the ``tag2size`` function.

    Examples
    --------
    >>> from raisin.serialization.core import size2tag
    >>> p_bin = lambda flag: ', '.join(bin(o) for o in flag)
    >>>
    >>> size2tag(0)
    b'\x80'
    >>> p_bin(_)
    '0b10000000'
    >>> size2tag(1)
    b'\x81'
    >>> p_bin(_)
    '0b10000001'
    >>> size2tag(127)
    b'\xff'
    >>> p_bin(_)
    '0b11111111'
    >>> size2tag(128)
    b'\x01\x80'
    >>> p_bin(_)
    '0b1, 0b10000000'
    >>> size2tag(2**(7*3))
    b'\x01\x00\x00\x80'
    >>> p_bin(_)
    '0b1, 0b0, 0b0, 0b10000000'
    >>>
    """
    if size == 0:
        return b'\x80'
    flags_list = []
    while size:
        size, rest = divmod(size, 2 ** 7)
        flags_list.append(rest)
    flags_list.reverse()
    flags_list[-1] += 1 << 7
    return bytes(flags_list)


def tag2size(*, pack=b'', gen=(lambda: (yield from []))()):
    r"""
    ** Allows to find the number encoded in a flag. **

    Parameters
    ----------
    pack : bytes
        The first package of the *gen* generator.
        Must contain the beginning of the flag.
    gen : generator
        The generator that contains the sequence of bytes
        if they are not all specified in *pack*.

    Returns
    -------
    size : int
        The length represented by the flag.
    pack : bytes
        The entry package without the flag.
    gen : generator
        The *gen* generator possibly slightly iterated.

    Raises
    ------
    StopIteration
        If the flag is incomplete.

    Notes
    -----
    This is the bijection of the ``tag2size`` function.

    Examples
    --------
    >>> from raisin.serialization.core import tag2size
    >>>
    >>> tag2size(pack=b'\x80')[0]
    0
    >>> tag2size(pack=b'\x81')[0]
    1
    >>> tag2size(pack=b'\xff')[0]
    127
    >>> tag2size(pack=b'\x01\x80')[0]
    128
    >>> tag2size(pack=b'\x01\x00\x00\x80')[0]
    2097152
    >>>
    """
    gen = iter(gen)
    size = 0
    while True:
        if pack:
            octet, pack = pack[0], pack[1:]
        else:
            while not pack:
                pack = next(gen)
            octet, pack = pack[0], pack[1:]
        if octet & 0b10000000:  # if we reach the end of the flag
            size = (size << 7) + (octet - 0b10000000)
            return size, pack, gen
        size = (size << 7) + octet


def get_header(*, pack=b'', gen=(lambda: (yield from []))()):
    r"""
    ** Retrieves the name of the header of a serialized object. **

    Leve une ValueError si l'entete n'est pas correcte.

    Parameters
    ----------
    pack : bytes
        The first package of the *gen* generator.
        Must contain the beginning of the header.
    gen : generator
        The generator that contains the sequence of bytes
        if they are not all specified in *pack*.

    Returns
    -------
    header : str
        The name of the header. This is a dictionary key *HEADER*.
    pack : bytes
        The entry package without the flag.
    gen : generator
        The *gen* generator possibly slightly iterated.

    Raises
    ------
    ValueError
        In case the header is not valid or incomplete.

    Examples
    --------
    >>> from raisin.serialization.core import get_header
    >>>
    >>> get_header(pack=b'/pickle/')[0]
    'pickle'
    >>> get_header(pack=b'\x00')[0]
    'pickle'
    >>> get_header(pack=b'/pickle/and ...')[0]
    'pickle'
    >>>
    """
    gen = iter(gen)
    bytes_header = b''
    while True:
        while not pack:
            try:
                pack = next(gen)
            except StopIteration as err:
                raise ValueError(f'the header is too short: {bytes_header}') from err
        bytes_header += pack[:1]
        pack = pack[1:]
        try:
            return BYTES2HEADER[bytes_header], pack, gen
        except KeyError as err:
            if not HEADERLEN[len(bytes_header)]:
                raise ValueError(
                    f'the bytes sequence {bytes_header} does not ' 'correspond to any known header.'
                ) from err
