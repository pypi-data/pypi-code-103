#!/usr/bin/env python3

"""
** Manages the serialization of python objects. **
--------------------------------------------------

This is where we take care of bijectively converting abstract python objects
into a sequence of bytes.
This is also where we take care of data compression and encryption.

Notes
-----
The functions accessible here are high-level APIs that do the input checks.
For a more intensive use where the inputs are checked,
it is better to go directly to the 'low level' functions.
"""

import re

__all__ = ['deserialize', 'dump', 'dumps', 'load', 'loads', 'serialize']


def deserialize(data, **kwargs):
    """
    ** Deserializes the encoded object by a *raisin* serialization function. **

    Parameters
    ----------
    data
        Data from a serialization function. They can take different forms:

        - *bytes* : Recommended for small objects.
            For large objects, RAM may be a limiting factor.
        - *generator of bytes* : This is the recommended form because it is the most effective.
            It allows to minimize the calculations while preserving the RAM.
            For example it can be the output of the ``serialize`` function.
        - *str* : Not recommended because it is not very effective.
            It's better if you do the conversion to bytes yourself.
        - *file like* : Must have a read() method that takes
            an integer argument and returns bytes or str. Thus *file* can be a
            binary file object opened for reading, an io.BytesIO object, or any
            other custom object that meets this interface.
    psw: str or bytes or None, default=None
        - *str* : Password for symmetric AES deciphering.
        - *bytes* : Public RSA key in PEM format.
        - *None* : Do not attempt any deciphering.
    paralleling_rate : int, default=0
        Allows you to parrallelize the calculations :

        - *0* : No parallelization, everything is executed in the current process.
        - *1* : Slight parallelization that creates several threads with the *threading* modules.
        - *2* : Parallelization that uses the different cores of the machine
            with the 'multiprocessing' module.

    Returns
    -------
    object
        The initially serialized python object.
        It is not the same instance as the initial object but the returned object
        is equivalent to the initial one.

    Examples
    --------
    >>> from raisin.serialization import deserialize
    >>> deserialize(b'/small int/123456789')
    123456789
    >>>
    """
    kwargs['psw'] = kwargs.get('psw', None)
    kwargs['paralleling_rate'] = kwargs.get('paralleling_rate', 0)

    assert isinstance(data, (bytes, str)) or hasattr(data, '__iter__') or hasattr(data, 'read')
    assert isinstance(kwargs['paralleling_rate'], int)
    assert 0 <= kwargs['paralleling_rate'] <= 2

    if kwargs['psw'] is not None:
        if isinstance(kwargs['psw'], bytes):
            try:
                if not re.search(
                    r'-----BEGIN RSA PRIVATE KEY-----(.|\n)+-----END RSA PRIVATE KEY-----',
                    kwargs['psw'].decode(),
                ):
                    raise ValueError('The key is not a private key in PEM format.')
            except UnicodeDecodeError as err:
                raise ValueError(
                    'If it is of type (bytes), the password must be an RSA '
                    'private key in PEM format, this is not the case.'
                ) from err
        elif isinstance(kwargs['psw'], str):
            if kwargs['psw'] == '':
                raise ValueError(
                    'The password should not be an empty string, '
                    'if there is no password, it should not be specified.'
                )
        else:
            raise TypeError("'psw' have to be str or bytes.")

    from raisin.serialization.iter_tools import data2gen

    pack, gen = data2gen(data)
    from raisin.serialization.core import deserialize as deserialize_

    return deserialize_(pack, gen, **kwargs)


def dump(obj, file, **kwargs):
    """
    ** Write a representation of obj to the open file object file. **

    This function is an overlay of the ``serialize`` function,
    but may be more efficient.

    Parameters
    ----------
    obj
        The object to serialize.
    file
        The *file* argument must have a write() method that accepts a single
        bytes argument. It can thus be a file object opened for binary
        writing, an io.BytesIO instance, or any other custom object that meets
        this interface.
    **kwargs : dict, optional
        These are the arguments directly transferred to the ``serialize`` function.
        Only the 'compresslevel' parameter differs, because here the default value is 5.

    See Also
    --------
    serialize : Main function for 'low level' serialization.

    Examples
    --------
    >>> import tempfile
    >>> from raisin.serialization import dump
    >>> with tempfile.TemporaryFile('wb') as file:
    ...     dump(123456789, file)
    ...
    >>>
    """
    assert hasattr(file, 'write')
    for pack in serialize(obj, **kwargs):
        file.write(pack)


def dumps(obj, **kwargs):
    """
    ** Serialize an object and return a nice string. **

    This function is an overlay of the ``serialize`` function.
    Instead of yielding a string of bytes, this function
    retrieves a simple printable ascii string.
    The number of characters given by this function tends
    asymptotically to be 64/51 larger than the number of bytes
    given by the ``serialize`` function.

    Parameters
    ----------
    obj
        The object to serialize.
    **kwargs : dict, optional
        These are the arguments directly transferred to the ``serialize`` function.
        Only the 'compresslevel' parameter differs, because here the default value is 1.

    Returns
    -------
    str
        A printable ascii character string. This string can be used as input
        parameter to the 'loads' function. But this protocol is also compatible
        with the 'load' and 'deserialize' functions.

    See Also
    --------
    serialize : Main function for 'low level' serialization.
    dump : Allows to serialize efficiently in a file.

    Examples
    --------
    >>> from raisin.serialization import dumps
    >>> dumps(123456789)
    '00aWDBam0vc'
    >>>
    """
    kwargs['compresslevel'] = kwargs.get('compresslevel', 1)
    from raisin.serialization.core import bytes2str
    from raisin.serialization.constants import HEADER

    return HEADER['dumps'][1].decode(encoding='ascii') + bytes2str(serialize(obj, **kwargs))


def load(file, **kwargs):
    """
    ** Bijection of the 'dump' function. **

    Allows to reconstitute aserialized object in a file.

    Parameters
    ----------
    file
        The argument *file* must have a read() method that takes
        an integer argument and returns bytes or str. Thus *file* can be a
        binary file object opened for reading, an io.BytesIO object, or any
        other custom object that meets this interface.
    **kwargs : dict
        These are the arguments directly transferred to the ``deserialize`` function.

    Returns
    -------
    object
        The initially serialized python object.
        It is not the same instance as the initial object but the returned object
        is equivalent to the initial one.

    Examples
    --------
    >>> from os.path import join
    >>> from tempfile import mkdtemp
    >>> from raisin.serialization import dump, load
    >>>
    >>> filepath = join(mkdtemp(), 'object.rsn')
    >>> with open(filepath, 'wb') as file:
    ...     dump(123456789, file)
    ...
    >>> with open(filepath, 'rb') as file:
    ...     obj = load(file)
    ...
    >>> obj
    123456789
    >>>
    """
    assert hasattr(file, 'read')
    return deserialize(file, **kwargs)


def loads(string, **kwargs):
    """
    ** Bijection of the 'dumps' function. **

    Allows to reconstitute an object serialized by the 'dumps' function.

    Parameters
    ----------
    string : str
        The ascii string from the 'dumps' function.
    **kwargs : dict
        These are the arguments directly transferred to the ``deserialize`` function.

    Returns
    -------
    object
        The initially serialized python object.
        It is not the same instance as the initial object but the returned object
        is equivalent to the initial one.

    Examples
    --------
    >>> from raisin.serialization import loads
    >>> loads('00aWDBam0vc')
    123456789
    >>>
    """
    assert isinstance(string, str)
    return deserialize(string.encode('ascii'), **kwargs)


def serialize(obj, **kwargs):
    """
    ** Main function to serialize a python object. **

    Unlike 'pickle', this function supports a wider variety of objects.
    It serializes in real time by working on batches of data.
    RAM is therefore highly preserved even when multi-GB objects are serialized.

    Parameters
    ----------
    obj
        The object to serialize.
    compresslevel : int, default=0
        Allows lossless compression of the result in order to reduce the size
        of the transferred data. Can take the following values :

        - *-1* : Adaptive compression rate that provides optimal compression
            in a rate-limited communication channel.
            Works only if *parralelization_rate* > 0.
        - *0* : There is no compression.
        - *1* : Chose more compact tags but more difficult to interpret by a human.
            This is not a compression that tries to eliminate redundancy but only
            tries not to add more.
        - *2* : Light but fast compression.
            It is a good compromise between the time lost and the data rate gained.
        - *3* : Strong enough compression that aims for a compression ratio
            equal to 95% of the maximum compression ratio.
        - *4* : Maximum compression that does not care about the amount of resources.
    copy_file : boolean, default=True
        In case *obj* is a path_like to a file, the file itself is serialized (if True).
        Whatever the value of *copy_file*, *obj* remains unchanged.
    psw : str or bytes or None, default=None
        Allows you to ciffer the return value :

        - *str* : Symmetric ciphering with the AES algorithm.
        - *bytes* : Public key in PEM format, RSA is used.
        - *None* : No ciphering.
    authenticity : boolean, default=False
        Adds a chriptographic hash (if True). This ensures that the data is authentic.
    paralleling_rate : int, default=0
        Allows you to parrallelize the calculations :

        - *0* : No parallelization, everything is executed in the current process.
        - *1* : Slight parallelization that creates several threads with the *threading* modules.
        - *2* : Parallelization that uses the different cores of the machine
            with the 'multiprocessing' module.

    Yields
    ------
    bytes
        The concatenation of all ceded packages contains sufficient
        information to reconstruct the original object.

    Examples
    --------
    >>> from raisin.serialization import serialize
    >>>
    """
    kwargs['compresslevel'] = kwargs.get('compresslevel', 0)
    kwargs['copy_file'] = kwargs.get('copy_file', True)
    kwargs['psw'] = kwargs.get('psw', None)
    kwargs['authenticity'] = kwargs.get('authenticity', (kwargs['psw'] is not None))
    kwargs['paralleling_rate'] = kwargs.get('paralleling_rate', 0)

    assert isinstance(kwargs['compresslevel'], int)
    assert isinstance(kwargs['copy_file'], bool)
    assert isinstance(kwargs['authenticity'], bool)
    assert isinstance(kwargs['paralleling_rate'], int)
    if kwargs['psw'] is not None:
        if isinstance(kwargs['psw'], bytes):
            try:
                if not re.search(
                    r'-----BEGIN PUBLIC KEY-----(.|\n)+-----END PUBLIC KEY-----',
                    kwargs['psw'].decode(),
                ):
                    raise ValueError('The key is not a public key in PEM format.')
            except UnicodeDecodeError as err:
                raise ValueError(
                    'If it is of type (bytes), the password must be an RSA public '
                    'key in PEM format, this is not the case'
                ) from err
        elif isinstance(kwargs['psw'], str):
            if kwargs['psw'] == '':
                raise ValueError(
                    'The password should not be an empty string, '
                    'if there is no password, it should not be specified.'
                )
        else:
            raise TypeError("'psw' have to be str or bytes.")
    assert -1 <= kwargs['compresslevel'] <= 4
    assert 0 <= kwargs['paralleling_rate'] <= 2

    from raisin.serialization.core import serialize

    yield from serialize(obj, **kwargs)
