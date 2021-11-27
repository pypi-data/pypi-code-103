"""Declares :class:`CipherText`."""


class Ciphertext:
    """The base class for all encryption results."""
    __module__ = 'unimatrix.ext.crypto'
    NotDecryptable = type('NotDecryptable', (Exception,), {})

    def __init__(self, ct, algorithm):
        self.__ct = ct
        self.__algorithm = algorithm

    async def decrypt(self, key):
        return await self.__algorithm.decrypt(key, self)

    def __bytes__(self):
        return self.__ct
