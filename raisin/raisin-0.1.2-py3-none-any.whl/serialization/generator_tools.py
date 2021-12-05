#!/usr/bin/env python3

"""
** Offers small and simple tools to help manage generators. **
--------------------------------------------------------------

More specifically, these are functions dedicated to flow management
for serialization and deserialization.
"""

import tempfile

from raisin.serialization.constants import BUFFER_SIZE


class _Null:
    """
    Stratagem to find out if a default setting is provided.
    """

def anticipate(gen):
    """
    ** Allows to know if the ceded packet is the last one. **

    Parametres
    ----------
    gen : iterable
        Generator of unknown 'length', which gives away objects of unknown length.

    Yields
    ------
    is_end : boolean
        A boolean which is True if the packet is the last one, False otherwise.
    pack
        The packet given up by the input generator.

    Raises
    ------
    ValueError
        In case there are no packages to count.

    Notes
    -----
    There is no verification on the entries.

    Examples
    --------
    >>> from raisin.serialization.generator_tools import anticipate
    >>>
    >>> for is_end, pack in anticipate(range(3)):
    ...     print(is_end, pack)
    ...
    False 0
    False 1
    True 2
    >>> list(anticipate(['pack']))
    [(True, 'pack')]
    >>>
    """
    is_empty = True
    current = None

    for i, current in enumerate(gen):
        if i == 0:
            previous = current
            is_empty = False
            continue
        yield False, previous
        previous = current

    if is_empty:
        raise ValueError('The generator must not be empty.')
    yield True, current

def concat_gen(gen):
    r"""
    ** Add flags so that you can find the current division. **

    Goes together with the ``deconcat_gen`` function.

    Parameters
    ----------
    gen : generator
        Bytes string generator.

    Yields
    ------
    bytes
        The same packet as the input generator with a flag that
        gives the length of the packet.

    Examples
    --------
    >>> from raisin.serialization.generator_tools import concat_gen
    >>>
    >>> gen = [b'a', b'houla', b'', b'hihi']
    >>> b''.join(concat_gen(gen))
    b'\x81a\x85houla\x80\x84hihi'
    >>>
    """
    from raisin.serialization.core import size2tag
    yield from (size2tag(len(e)) + e for e in gen)

def data2gen(data):
    """
    ** Transforms the input into a byte generator. **

    Parameters
    ----------
    data
        A serialized object that can take various forms:

        - *bytes* : The entrance is returned as it was.
        - *generator* : The generator must yield strings of bytes or characters.
        - *BufferedReader* : The content of the file is transferred in packages.
        - *str* : (not recommended) The string must be encoded in ascii.
            The binary representation of the string is returned.
        - *TextIOWrapper* : (not recommended) The ascii content of the
            file is transferred in packages.

    Returns
    -------
    bytes
        A packet of bytes that precedes the generator.
    generator
        A byte chain generator.

    Raises
    ------
    ValueError
        In case a string is not written entirely in ascii.
    TypeError
        If the input is not convertible into a byte generator.

    Examples
    --------
    >>> from raisin.serialization.generator_tools import data2gen
    >>>
    >>> pack, gen = data2gen(b'bytes string')
    >>> pack, list(gen)
    (b'bytes string', [])
    >>> pack, gen = data2gen('str string')
    >>> pack, list(gen)
    (b'str string', [])
    >>> pack, gen = data2gen(iter([b'a generator']))
    >>> pack, list(gen)
    (b'', [b'a generator'])
    >>>
    """
    def _file_like(data):
        while True:
            pack = data.read(BUFFER_SIZE)
            if pack:
                if isinstance(pack, bytes):
                    yield pack
                else:
                    try:
                        yield pack.encode(encoding='ascii')
                    except UnicodeEncodeError as err:
                        raise ValueError('If you want to deserialize a txt file '
                                         '(which is not recommended), this file '
                                         'must be written entirely in ascii.'
                                         ) from err
            else:
                break

    def _iter(data):
        for pack in data:
            if isinstance(pack, bytes):
                yield pack
            elif isinstance(pack, str):
                try:
                    yield pack.encode(encoding='ascii')
                except UnicodeEncodeError as err:
                    raise ValueError('If you want to deserialize a string generator. '
                                      'The strings must be written entirely in ascii.'
                                     ) from err
            else:
                raise TypeError('The packets given by the generator must be of type '
                                 f'str or bytes, not {pack.__class__.__name__}.')

    if isinstance(data, bytes):
        return data, (lambda:(yield from []))()
    if isinstance(data, str):
        try:
            return data.encode(encoding='ascii'), (lambda:(yield from []))()
        except UnicodeEncodeError as err:
            raise ValueError('if you want to deserialize a string, the string '
                              'must be written entirely in ascii.'
                             ) from err
    elif hasattr(data, 'read'):
        return b'', _file_like(data)
    elif hasattr(data, '__iter__'):
        return b'', _iter(data)
    else:
        raise TypeError('The argument provided is not in a supported type.')

def deconcat_gen(*, pack=b'', gen=(lambda:(yield from []))()):
    r"""
    ** Reconcile and re-cut the packets to their original shape. **

    Goes together with the ``concat_gen`` function.

    Parameters
    ----------
    pack : bytes
        The first element of the generator.
    gen : generator
        The rest of the packages to be rearranged.

    Yields
    ------
    bytes
        The reordered packages like the ones that were once provided
        at the input of the ``concat_gen`` function.

    Raises
    ------
    ValueError
        If there is an inconsistency in the packages.

    Examples
    --------
    >>> from raisin.serialization.generator_tools import deconcat_gen
    >>> list(deconcat_gen(pack=b'\x81a\x85houla\x80\x84hihi'))
    [b'a', b'houla', b'', b'hihi']
    >>> list(deconcat_gen(gen=[b'\x81a\x85ho', b'ula\x80\x84hihi']))
    [b'a', b'houla', b'', b'hihi']
    >>>
    """
    from raisin.serialization.core import tag2size
    n_pack = 0

    while True:
        # length recovery
        n_pack += 1
        try:
            size, pack, gen = tag2size(pack=pack, gen=gen)
        except ValueError as err:
            raise ValueError('error in the header of package number '
                            f'{n_pack}. The flag is corrupted.') from err
        except StopIteration:
            break

        # concatenation of the enough number of data
        while len(pack) < size:
            try:
                pack += next(gen)
            except StopIteration as err:
                raise ValueError(
                    f'The package number {n_pack} is incomplete.\n'
                    f'Expected length: {size}\n'
                    f'Available length: {len(pack)}') from err

        # truncation to the exact length
        yield pack[:size]
        pack = pack[size:]

def relocate(gen):
    """
    ** Exhausts the input generator, identity function. **

    Parameters
    ----------
    gen : generator
        A byte string generator.

    Returns
    -------
    generator
        A kind of copy of the generator *gen*.

    Notes
    -----
    If the cumulative size of the data transferred by the *gen* generator
    does not exceed *BUFFER_SIZE*, then the buffering is done in RAM,
    otherwise the packets are stored in a temporary file in order to preserve RAM.

    Examples
    --------
    >>> from raisin.serialization.generator_tools import relocate
    >>>
    >>> gen = iter([b'a', b'b'])
    >>> next(gen)
    b'a'
    >>> gen_copy = relocate(gen)
    >>> next(gen)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    StopIteration
    >>> next(gen_copy)
    b'b'
    >>>
    """
    # the garbage collector is responsible for closing the file
    file = tempfile.SpooledTemporaryFile(max_size=BUFFER_SIZE, mode='w+b')
    for pack in concat_gen(gen):
        file.write(pack)
    file.seek(0)
    pack, gen = data2gen(file)
    return deconcat_gen(pack=pack, gen=gen)

def to_gen(*, pack=_Null, gen=(lambda:(yield from []))(), size=BUFFER_SIZE):
    r"""
    ** Normalize the size of the packages. **

    Group the ceded packets by 'gen' in order to cede packets
    of normalized length.

    Parameters
    ----------
    pack : bytes
        The first pack.
    gen : generator
        The generator that assigns the sequence of pack.
    size : int or None, default=BUFFER_SIZE
        Size of yieled packages (if int).
        (if None), just make a generator whose first element is 'pack'.
        All the packets transferred are then identical to those of
        the input generator.

    Yields
    ------
    bytes
        A packet of size *size*, created by concatenating the input data.

    Notes
    -----
    There is no verification on the entries.

    Examples
    --------
    >>> import random
    >>> from raisin.serialization.generator_tools import to_gen
    >>>
    >>> random.seed(0)
    >>>
    >>> l = [b'\x00'*random.randint(0, 1000) for i in range(4)]
    >>> [len(e) for e in l]
    [864, 394, 776, 911]
    >>>
    >>> [len(e) for e in to_gen(gen=l, size=500)]
    [500, 500, 500, 500, 500, 445]
    >>> [len(e) for e in to_gen(pack=b'', gen=l, size=500)]
    [500, 500, 500, 500, 500, 445]
    >>> [len(e) for e in to_gen(pack=b'\x00'*55, gen=l, size=500)]
    [500, 500, 500, 500, 500, 500]
    >>> [len(e) for e in to_gen(pack=b'\x00'*56, gen=l, size=500)]
    [500, 500, 500, 500, 500, 500, 1]
    >>>
    >>> [len(e) for e in to_gen(gen=l, size=None)]
    [864, 394, 776, 911]
    >>> [len(e) for e in to_gen(pack=b'\x00'*55, gen=l, size=None)]
    [55, 864, 394, 776, 911]
    >>> [len(e) for e in to_gen(pack=b'', gen=l, size=None)]
    [0, 864, 394, 776, 911]
    >>>
    """
    if size is None:
        if pack is not _Null:
            yield pack
        yield from gen
    else:
        if pack is _Null:
            pack = b''
        else:
            while len(pack) > size:
                yield pack[:size]
                pack = pack[size:]
        for data in gen:
            pack += data
            while len(pack) > size:
                yield pack[:size]
                pack = pack[size:]
        yield pack
