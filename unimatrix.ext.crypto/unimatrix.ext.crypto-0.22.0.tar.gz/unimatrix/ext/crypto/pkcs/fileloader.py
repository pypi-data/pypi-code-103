"""Declares :class:`FileLoader`."""
import os

from unimatrix.lib.datastructures import DTO

from ..keyloader import KeyLoader
from .rsaprivatekey import RSAPrivateKey


class FileLoader(KeyLoader):
    """
    An example configuration is shown below:

    .. code:: python

        {
            'loader': "unimatrix.ext.crypto.pkcs.FileLoader",
            'keys': [
                {
                    "path": "/path/to/key",
                    "keyid": "<optional, if omitted the key filename is used.>",
                    'password': "<optional, if the key has a password>"
                }
            ]
        }
    """
    pem_headers = {
        b'-----BEGIN RSA PRIVATE KEY-----': RSAPrivateKey
    }

    def setup(self, opts):
        self.keys = []
        for key in opts.get('keys') or []:
            _, fn = os.path.split(key.path)
            self.keys.append(DTO.fromdict({
                'keyid': opts.get('keyid') or fn,
                'path': key.path,
                'password': key.get('password'),
                'public_only': key.get('public_only') or False
            }))

    async def list(self):
        for key in self.keys:
            content = open(key.path, 'rb').read()
            header, *_ = bytes.splitlines(content)
            if header not in self.pem_headers:
                raise NotImplementedError
            cls = self.pem_headers[header]
            yield cls({'content': content}, keyid=key.keyid)
