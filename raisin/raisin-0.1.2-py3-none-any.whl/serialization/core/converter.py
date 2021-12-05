#!/usr/bin/env python3

"""
** Allows to switch from bytes to ascii and vice versa. **
----------------------------------------------------------

It is on this module that the ``raisin.serialization.dumps``
and ``raisin.serialization.loads`` functions are based.
"""

from raisin.serialization.constants import (ALPHABET, BUFFER_SIZE, HEADER,
    N_BYTES, N_SYMB)
from raisin.serialization.tools import anticipate, get_header, to_gen


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

    Examples
    --------
    >>> from raisin.serialization.core.converter import bytes2str
    >>> bytes2str([b'toto'])
    '0Dg90aabVb'
    >>> bytes2str([b'\x00'*10]*4)
    '1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaO'
    >>>
    """
    def int_to_alph(i, n_symb, n_car):
        """
        Convertie un entier en une string
        constitue par des symboles de l'alphabet.
        contraintes:
            i <= n_car**n_symb
            retourne n_symb caracteres
        """
        string = ''
        while i:
            i, r = divmod(i, n_car)
            string = ALPHABET[r] + string
        string = ALPHABET[0]*(n_symb-len(string)) + string
        return string

    def pack_to_int(pack):
        """
        Converti une string binaire en un entier.
        """
        return int.from_bytes(pack, byteorder='big', signed=False)

    # preparation (n_car**n_symb >= n2**n_bytes)
    pack = b''.join(gen)
    if len(pack) < N_BYTES*3/4: # Si il vaut mieu ne pas faire des packets trop gros.
        sortie = HEADER['small dumps'][1].decode()
        n_car = 64 # Nbr de caracteres differents.
        n_bytes = 3 # C'est le nombre d'octet que l'on regroupe.
        n_symb = 4 # On converti 3 octets en 4 caracteres.
    else:
        sortie = HEADER['large dumps'][1].decode()
        n_car = len(ALPHABET) # Nbr de caracteres differents.
        n_bytes = N_BYTES # C'est le nombre d'octet que l'on regroupe.
        n_symb = N_SYMB # Regroupe N_BYTES octets en N_SYMB caracteres.

    # convertion
    for is_end, pack in anticipate(to_gen(pack=pack, size=n_bytes)):
        sortie += int_to_alph(
            pack_to_int(pack),
            n_symb,
            n_car)
        if is_end and len(pack) < n_bytes:
            return sortie + ALPHABET[len(pack)]
    return sortie

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

    Examples
    --------
    >>> from raisin.serialization.core.converter import str2bytes
    >>> str2bytes('0Dg90aabVb')
    b'toto'
    >>>
    """
    def alph_to_int(phrase, n_car, index):
        """
        Converti une string constitue par des
        symboles de l'alphabet en entier.
        """
        i = 0
        for rang, symb in enumerate(reversed(phrase)):
            i += index[symb] * n_car**rang
        return i

    def int_to_pack(i, n_bytes):
        """
        Converti un entier en une string binaire.
        Retourne 'n_bytes' octets.
        """
        return i.to_bytes(n_bytes, byteorder="big", signed=False)

    def alph_to_pack(phrases, n_car, index, n_bytes):
        """
        Convertie tous les blocs d'un coup pour plus de
        performance
        """
        return b''.join([
            int_to_pack(
                alph_to_int(phrase, n_car, index),
                n_bytes
            )
            for phrase in phrases
        ])

    # preparation (n_car**n_symb >= n2**n_bytes)
    head, gen, pack = get_header(pack=string.strip().encode('ascii'))
    string = (pack + b''.join(gen)).decode('ascii')
    index = {symb: i for i, symb in enumerate(ALPHABET)}
    if head == 'small dumps':
        n_car = 64 # Nbr de caracteres differents.
        n_bytes = 3 # C'est le nombre d'octet que l'on regroupe.
        n_symb = 4 # On converti 3 octets en 4 caracteres.
    elif head == 'large dumps':
        n_car = len(ALPHABET) # Nbr de caracteres differents.
        n_bytes = N_BYTES # C'est le nombre d'octet que l'on regroupe.
        n_symb = N_SYMB # Regroupe N_BYTES octets en N_SYMB caracteres.
    else:
        raise ValueError(
            "L'entete ne peut etre que 'small dumps' ou " \
            + "'large dumps'. Pas {}.".format(head))

    # desencapsulation
    data = b''
    phrases = []
    bloc = BUFFER_SIZE // n_bytes
    for i, (is_end, phrase) in enumerate(anticipate(to_gen(pack=string, size=n_symb))):
        if is_end and len(phrase) < n_symb:
            data += alph_to_pack(phrases, n_car, index, n_bytes)
            data = data[:-n_bytes] + data[-alph_to_int(phrase, n_car, index):]
            return data
        phrases.append(phrase)
        if not i % bloc:
            data += alph_to_pack(phrases, n_car, index, n_bytes)
            phrases = []
    data += alph_to_pack(phrases, n_car, index, n_bytes)
    return data
