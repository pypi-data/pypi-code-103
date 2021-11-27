"""Create a JSON Web Signature (JWS) using the default signer."""
import os
from unimatrix.ext import crypto


os.environ.setdefault('SECRET_KEY', 'my very secret key')

signer = crypto.get_signer()
jws = crypto.JSONWebSignature(
    crypto.JSONWebToken({'foo': 'bar'})
)
signature = jws.sign(signer)

assert signature.verify(signer.key)
