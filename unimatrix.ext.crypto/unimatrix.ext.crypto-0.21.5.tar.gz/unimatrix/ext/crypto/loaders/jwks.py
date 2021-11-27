"""Declares :class:`JWKSLoader`."""
import json
import logging

import aiohttp

from .base import BaseLoader
from ..trustedpublickey import TrustedPublicKey


class JWKSLoader(BaseLoader):
    """Loads public keys from an URL serving a JSON Web Key
    Set.
    """
    logger = logging.getLogger('unimatrix.ext.crypto')

    def setup(self, opts):
        self.url = opts.url

    async def load(self):
        return await self.get_jwks(self.url) or []

    async def get_jwks(self, url):
        keys = []
        async with aiohttp.ClientSession() as session:
            for jwk in ((await self.get(session, url) or {}).get('keys') or []):
                try:
                    keys.append(TrustedPublicKey.fromjwk(jwk))
                    if jwk.get('use') == 'sig':
                        assert keys[-1].can_verify() # nosec
                except (ValueError, AttributeError, TypeError) as e:
                    self.logger.error(
                        'Invalid JWK received from %s: %s',
                        self.server, repr(e)
                    )
                    continue

        return keys

    async def get(self, session, url):
        try:
            response = await session.get(url)
        except aiohttp.client_exceptions.ClientConnectorError:
            # Some error occurred when connecting, timeout or domain
            # not resolvable.
            self.logger.error(
                "Unable to connect load JWKS from %s", url)
            return
        if response.status != 200:
            self.logger.error(
                "Non-200 response from server (%s) GET %s",
                response.status, url)
            return
        try:
            return json.loads(await response.text())
        except ValueError:
            self.logger.error(
                "Parsing error: %s", url
            )
            return
