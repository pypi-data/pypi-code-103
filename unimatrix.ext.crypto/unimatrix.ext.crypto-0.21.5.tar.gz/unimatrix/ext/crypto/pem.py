"""Declares funcions to load keys from PEM."""
from typing import Union

from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends.openssl import ec
from cryptography.hazmat.backends.openssl import rsa

from .pkcs import RSAPrivateKey
from .pkcs import RSAPublicKey
from .ec import EllipticCurvePrivateKey
from .ec import EllipticCurvePublicKey
from .private import PrivateKey
from .public import PublicKey


CRYPTO_CLASSMAP = {
    ec._EllipticCurvePublicKey: EllipticCurvePublicKey,
    ec._EllipticCurvePrivateKey: EllipticCurvePrivateKey,
    rsa._RSAPrivateKey: RSAPrivateKey,
    rsa._RSAPublicKey: RSAPublicKey
}


def frompem(
    content: bytes,
    public: bool = True
) -> Union[PrivateKey, PublicKey]:
    """Inspect `content` and return the appropriate
    :class:`~unimatrix.ext.crypto.PrivateKey` or
    :class:`~unimatrix.ext.crypto.PublicKey` implementation.

    If `public` is ``True``, always return the public key.
    """
    kwargs = {}
    if isinstance(content, str):
        content = str.encode(content)
    if b'PUBLIC KEY' in content:
        load = load_pem_public_key
    elif b'PRIVATE KEY' in content:
        load = load_pem_private_key
        kwargs = {'password': None}
    else:
        raise ValueError("Cannot determine key type.")
    key = load(content, **kwargs)
    cls = CRYPTO_CLASSMAP[type(key)]
    obj = cls.fromkey(key)\
        if hasattr(cls, 'fromkey')\
        else cls({'key': key})
    if not isinstance(obj, PublicKey) and public:
        obj = obj.get_public_key()
    return obj
