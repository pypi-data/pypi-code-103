"""Declares functions to parse keys."""
from unimatrix.lib.datastructures import ImmutableDTO

from . import ec
from . import pkcs


PUBLIC_KEY_ALGORITHMS = {
    'RSA'   : pkcs.RSAPublicKey,
    'EC'    : ec.EllipticCurvePublicKey
}


def parse_jwk(jwk: dict):
    jwk = ImmutableDTO.fromdict(jwk)
    if not jwk.get('kty'):
        raise ValueError('kty is required')
    if jwk.kty not in PUBLIC_KEY_ALGORITHMS:
        raise TypeError(f'Unsupported key type: {jwk.kty}')
    return PUBLIC_KEY_ALGORITHMS[jwk.kty].fromjwk(jwk)
