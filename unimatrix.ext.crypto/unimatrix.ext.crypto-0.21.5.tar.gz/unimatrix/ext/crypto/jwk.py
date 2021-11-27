"""JSON Web Key (JWK) utilities."""
from typing import Union

from .ec import EllipticCurvePublicKey
from .pkcs import RSAPublicKey
from .private import PrivateKey
from .public import PublicKey


KTY_CLASSMAP = {
    'EC': EllipticCurvePublicKey,
    'RSA': RSAPublicKey
}


def fromjwk(
    jwk: dict,
    public: bool = True
) -> Union[PrivateKey, PublicKey]:
    """Parse a key implementation from a JSON Web Key (JWK).
    Currently only public keys are supported.
    """
    if jwk.get('kty') not in ('RSA', 'EC'):
        raise ValueError("Unsupported key type: {jwk['kty']}")
    return KTY_CLASSMAP[ jwk['kty'] ].fromjwk(jwk)
