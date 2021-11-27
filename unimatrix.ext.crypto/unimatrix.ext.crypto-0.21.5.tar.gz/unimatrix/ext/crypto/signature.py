"""Declares :class:`Signature`."""
import abc

from unimatrix.lib.datastructures import ImmutableDTO

from .const import OID_MAPPING


class Signature(metaclass=abc.ABCMeta):
    """Provides the interface for digital signatures."""
    __module__ = 'unimatrix.ext.crypto'
    InvalidSignature = type('InvalidSignature', (Exception,), {})

    @property
    def algorithm(self):
        return self.__algorithm

    @property
    def keyid(self):
        return self.__keyid

    @property
    def metadata(self) -> ImmutableDTO:
        return self.__metadata

    def __init__(self, buf, algorithm, metadata=None, keyid=None):
        self.__data = buf
        self.__algorithm = algorithm
        self.__padding, self.__hashing = None, None
        self.__metadata = ImmutableDTO(metadata or {})
        self.__keyid = keyid
        if self.__algorithm in OID_MAPPING:
            self.__padding, self.__hashing = OID_MAPPING[algorithm]

    def to_bytes(self):
        """Return a binary representation of the signature."""
        return self.__data

    def verify(self, key, data: bytes, suppress=False) -> bool:
        """Verifies the :class:`Signature` using the given public key
        `key`.
        """
        is_valid = self.__algorithm.verify(key, self.__data, data)
        if not is_valid and not suppress:
            raise self.InvalidSignature
        return is_valid

    def __str__(self):
        return bytes.hex(self.to_bytes())

    def __bytes__(self):
        return self.to_bytes()
