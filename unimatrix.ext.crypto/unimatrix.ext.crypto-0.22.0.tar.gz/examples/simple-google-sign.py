#!/usr/bin/env python3
"""Set the environment variables ``AZURE_KEYVAULT_NAME``
and ``AZURE_KEY_NAME`` before running this script.
"""
import hashlib
import os

import unimatrix.runtime
from unimatrix.ext import crypto


async def main():
    name = os.getenv('GOOGLE_SIGNING_KEY_NAME')
    crypto.add({
        'name': name,
        'usage': ['sign'],
        'loader': {
            'backend': 'urn:unimatrix:cloud:google',
            'opts': {
                'project': os.getenv('GOOGLE_PROJECT'),
                'location': os.getenv('GOOGLE_KEYRING_LOCATION'),
                'keyring': os.getenv('GOOGLE_KEYRING_NAME'),
            }
        }
    })
    message = b'Hello world!'
    digest = hashlib.sha256(message).digest()
    signer = crypto.get_signer(crypto.SECP256K1SHA256, keyid=name)
    key = signer.get_public_key()
    sig = await signer.sign(digest)

    assert sig.verify(key, digest, True)
    assert not sig.verify(key, hashlib.sha256(b'wrong digest').digest(), True)
    assert signer.public_key.verify(bytes(sig), digest)


if __name__ == '__main__':
    unimatrix.runtime.execute(main)
