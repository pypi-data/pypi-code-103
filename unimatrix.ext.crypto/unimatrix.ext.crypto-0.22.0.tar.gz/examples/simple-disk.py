#!/usr/bin/env python3
"""Set the environment variables ``AZURE_KEYVAULT_NAME``
and ``AZURE_KEY_NAME`` before running this script.
"""
import os

import unimatrix.runtime
from unimatrix.ext import crypto


async def main():
    name = 'noop.rsa'
    crypto.load({
        'keys': {
            name: {
                'name': name,
                'usage': ['sign', 'encrypt'],
                'loader': {
                    'backend': 'pem:disk',
                    'opts': {
                        'dirname': 'pki/pkcs'
                    }
                }
            },
            'noop.ec': {
                'name': 'noop.ec',
                'usage': ['sign'],
                'loader': {
                    'backend': 'pem:disk',
                    'opts': {
                        'dirname': 'pki/pkcs'
                    }
                }
            }
        }
    })

    signer = crypto.get_signer(crypto.RSAPKCS1v15SHA256, keyid=name)
    message = b'Hello world!'
    digest = signer.digest(message)
    sig = await signer.sign(digest)
    key = signer.get_public_key()

    assert sig.verify(key, digest, True)
    assert not sig.verify(key, signer.digest(b'wrong'), True)
    assert signer.public_key.verify(bytes(sig), digest)


if __name__ == '__main__':
    unimatrix.runtime.execute(main)
