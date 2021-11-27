"""Specifies the algorithms available to the :mod:`unimatrix.ext.crypto`
package.

Encryption algorithms
+++++++++++++++++++++

.. py:attribute:: AES256GCM

    256-bit Advanced Encryption Standard (AES-256) in Galois Counter Mode (GCM).

.. py:attribute:: RSAOAEPSHA256

    RSA with Optimal Asymmetric Encryption Padding (OAEP) and hash
    algorithm SHA-256.

Signing algorithms
++++++++++++++++++

.. py:attribute:: HMACSHA224

    Hash-Based Message Authentication Code (HMAC) using SHA-224.

.. py:attribute:: HMACSHA256

    Hash-Based Message Authentication Code (HMAC) using SHA-256.

.. py:attribute:: HMACSHA384

    Hash-Based Message Authentication Code (HMAC) using SHA-384.

.. py:attribute:: HMACSHA512

    Hash-Based Message Authentication Code (HMAC) using SHA-512.

.. py:attribute:: RSAPKCS1v15SHA256

    RSA with PKCS#1 version 1.5 padding and hash algorithm SHA-256.

.. py:attribute:: RSAPKCS1v15SHA384

    RSA with PKCS#1 version 1.5 padding and hash algorithm SHA-384.

.. py:attribute:: RSAPKCS1v15SHA512

    RSA with PKCS#1 version 1.5 padding and hash algorithm SHA-512.

.. py:attribute:: SECP256K1SHA256

    Elliptic Curve Digital Signing Algorithm (ECDSA) with curve
    ``secp256k1`` (also known as ``P-256K``).

.. py:attribute:: SECP256R1SHA256

    Elliptic Curve Digital Signing Algorithm (ECDSA) with curve
    ``secp256r1`` (also known as ``P-256``).
"""
from .base import Algorithm
from .aes import *
from .ec import *
from .hmac import *
from .rsa import *


__all__ = [
    'HMACSHA224',
    'HMACSHA256',
    'HMACSHA384',
    'HMACSHA512',
    'RSAPKCS1v15SHA256',
    'SECP256K1SHA256',
    'SECP256R1SHA256'
]
