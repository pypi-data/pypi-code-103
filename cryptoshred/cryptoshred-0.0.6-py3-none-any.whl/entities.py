from enum import Enum
from functools import singledispatch
import json
from typing import Any, Callable, Generic, Optional, TypeVar, cast

from uuid import UUID, uuid4
from pydantic import BaseModel, UUID4, PrivateAttr
from pydantic.fields import Field
from cryptoshred.backends import KeyBackend

from cryptoshred.engines import AesEngine
from cryptoshred.exceptions import KeyNotFoundException

T = TypeVar("T", bound=object)
BM = TypeVar("BM", bound=BaseModel)


class CryptographicAlgorithm(str, Enum):
    """
    The available crypto algorithms.
    """

    aes_cbc = "AES"


class CryptoContainer(BaseModel, Generic[T]):
    """
    The CryptoContainer class implements the concept of a cryptoshreddable entity.

    Args:
        id (UUID4): Optional uuid of the key to use for decryption. Generated if not present
        enc (bytes): The encrypted value
        algo (CryptographicAlgorithm): The cryptographic algorithm used. Defaults to AES_CBC
        ksize (int): The key size used
        key_backend (KeyBackend): The backend used to look up keys
    """

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True  # TODO remove

    id: UUID4 = Field(default_factory=uuid4)
    enc: bytes = b""
    algo: CryptographicAlgorithm = CryptographicAlgorithm.aes_cbc
    ksize: int = 256
    _cached_value: Optional[T] = PrivateAttr(default=None)
    _key_backend: KeyBackend = PrivateAttr(default=None)

    def __init__(self, **data: object) -> None:
        super().__init__(**data)
        # TODO default key backend
        self._key_backend = cast(KeyBackend, data.get("key_backend"))

    def value(self, clazz: Callable[..., T]) -> Optional[T]:
        """
        Will return the contained value constructed using the constructor of the given class.

        Agrs:
            clazz (T): The class to deserialize the value to

        Returns:
            The value contained in the container passed through the constructor of the given class
        """
        if not self._cached_value:
            self._cached_value = self._decrypt(clazz)
        return self._cached_value

    def plain(self) -> str:
        """
        The contained value as string.

        Returns:
            The contained value
        """
        # The related mypy issue is tracked under:
        # https://github.com/python/mypy/issues/10518
        # https://github.com/python/mypy/issues/9253
        res = cast(str, self.value(str) or "")  # type: ignore
        return res

    def _decrypt(self, clazz: Callable[..., T]) -> Optional[T]:  # Py3.10 switch
        try:
            # TODO: Engine determination from container
            engine = AesEngine(self._key_backend)
            dt = engine.decrypt(cipher_text=self.enc, key_id=self.id)
            if clazz == str:
                return clazz(dt.decode("utf-8"))
            elif clazz == bytes:
                return clazz(dt)
            elif clazz == int:
                return clazz(int.from_bytes(dt, byteorder="big", signed=True))
            elif clazz == UUID:
                return clazz(bytes=dt)
            else:
                try:
                    return clazz(**json.loads(dt))
                except Exception:
                    return clazz(dt)
        except KeyNotFoundException:
            return None


@singledispatch
def container_for(
    value: Any, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[Any]:
    """
    Given a value and some configuration will return the cryptocontainer for
    that value. Specific typing is implemented via singledispatch.
    If no specific way to encode the value is available the implementation will
    fallback to calling ``bytes`` on the passed object.

    Args:
        value (T): The value to provide a cryptocontainer for
        id (UUID4): The subject id used to find the key. If ``None`` a new key will be generated
        key_backend (KeyBackend): The key backend to use for persistence

    Returns:
        The cryptocontainer containing the passed value
    """

    data = bytes(value)

    return _encrypt(data=data, id=id, key_backend=key_backend)


@container_for.register
def container_for_str(
    value: str, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[str]:
    """For strings"""

    data = bytes(value, "utf-8")

    return _encrypt(data=data, id=id, key_backend=key_backend)


@container_for.register
def container_for_bytes(
    value: bytes, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[bytes]:
    """For bytes"""

    return _encrypt(data=value, id=id, key_backend=key_backend)


@container_for.register
def container_for_base_model(
    value: BaseModel, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[BaseModel]:
    """For objects extending pydantics BaseModel"""

    data = bytes(value.json(), "utf-8")

    return _encrypt(data=data, id=id, key_backend=key_backend)


@container_for.register
def container_for_dict(
    value: dict, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[dict]:
    """For good old dictionaries"""

    data = bytes(json.dumps(value), "utf-8")

    return _encrypt(data=data, id=id, key_backend=key_backend)


@container_for.register
def container_for_list(
    value: list, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[list]:
    """For lists of any"""

    data = bytes(json.dumps(value), "utf-8")

    return _encrypt(data=data, id=id, key_backend=key_backend)


@container_for.register
def container_for_int(
    value: int, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[int]:
    """For integers"""

    data = value.to_bytes((value.bit_length() + 7) // 8, byteorder="big", signed=True)

    return _encrypt(data=data, id=id, key_backend=key_backend)


@container_for.register
def container_for_uuid(
    value: UUID, *, id: Optional[UUID] = None, key_backend: KeyBackend
) -> CryptoContainer[UUID]:
    """For UUIDs"""

    data = value.bytes

    return _encrypt(data=data, id=id, key_backend=key_backend)


def _encrypt(
    data: bytes, id: Optional[UUID], key_backend: KeyBackend
) -> CryptoContainer:
    engine = AesEngine(key_backend=key_backend)
    if not id:
        id = engine.generate_key()
    ct = engine.encrypt(data=data, key_id=id)
    return CryptoContainer(enc=ct, key_backend=key_backend, id=id)
