"""Declares various constants and mappings."""
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256


# Maps signature algorithm OIDs to constants from the cryptography module.
OID_MAPPING = {
    "1.2.840.113549.1.1.11": (PKCS1v15(), SHA256())
}


RSA_PKCS1_SHA256 = "1.2.840.113549.1.1.11"
