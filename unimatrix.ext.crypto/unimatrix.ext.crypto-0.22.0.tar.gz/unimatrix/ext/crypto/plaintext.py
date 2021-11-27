"""Declares :class:`Plaintext`."""


class Plaintext:
    """Represents the plain texts that is the input for an encryption
    algorithm.
    """
    __module__ = 'unimatrix.ext.crypto'

    def __init__(self, pt, encoding="utf-8"):
        self.__value = str.encode(pt, encoding) if isinstance(pt, str) else pt
        self.__encoding = encoding

    def __str__(self):
        return bytes.decode(self.__value, self.__encoding)

    def __bytes__(self):
        return self.__value
