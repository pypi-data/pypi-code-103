"""Create a signature using the secret key provided through the environment
variable ``SECRET_KEY``.
"""
import os
from unimatrix.ext import crypto


os.environ.setdefault('SECRET_KEY', 'my very secret key')

payload = b'Hello world!'
key = crypto.get_secret_key()
signer = crypto.get_signer()
signature = signer.sign(payload)

assert signature.verify(key, payload)
