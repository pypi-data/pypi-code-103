"""Declares :class:`EllipticCurveVerifier`."""
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import ec


class EllipticCurveVerifier:

    def verify(self,
        signature: bytes,
        digest: bytes,
        algorithm,
        *args, **kwargs
    ) -> bytes:
        try:
            self.public.verify(
                bytes(signature), digest,
                ec.ECDSA(utils.Prehashed(algorithm))
            )
            return True
        except InvalidSignature:
            return False
