"""Declares :class:`WellKnownOAuthLoader`."""
import json
import logging

import aiohttp
from unimatrix.conf import settings

from .base import BaseLoader
from ..trustedpublickey import TrustedPublicKey


class WellKnownOAuthLoader(BaseLoader):
    """Loads public keys from an OAuth 2.0 authorization server
    using the `.well-known/oauth-authorization-server` endpoint.
    It inspects the response for a ``jwks_uri`` member, holding
    a JSON Web Key Set, and imports the keys contained in the
    set.

    If the server does not respond, or either one of the URLs
    does not exist, or if there are errors importing the keys,
    the :class:`WellKnownOAuthLoader` silently fails.
    """
    default_path = '.well-known/oauth-authorization-server'
    logger = logging.getLogger('uvicorn')

    def setup(self, opts):
        self.server = str.rstrip(opts.server, '/')
        self.path = str.lstrip(opts.get('path') or self.default_path, '/')
        self.url = str.join('/', [self.server, self.path])

    async def load(self):
        return await self._get_jwks() or []

    async def _get_jwks(self):
        keys = []
        async with aiohttp.ClientSession() as session:
            dto = await self.get(session, self.url) or {}
            if not dto.get('jwks_uri'):
                self.logger.error("Could not determine JWKS URL from metadata")
                return
            for jwk in ((await self.get(session, dto['jwks_uri'])) or {})\
            .get('keys') or []:
                try:
                    keys.append(TrustedPublicKey.fromjwk(jwk))
                    if jwk.get('use') == 'sig':
                        assert keys[-1].can_verify() # nosec
                    self.logger.debug(
                        "Trusting public key (kid: %s, kty: %s, server: %s)",
                        jwk.get('kid'),
                        jwk.get('kty'),
                        self.server
                    )
                except (ValueError, AttributeError, TypeError) as e:
                    self.logger.error(
                        'Invalid JWK received from %s: %s',
                        self.server, repr(e)
                    )
                    continue

        self.logger.warning("Imported %s keys from %s", len(keys), self.server)
        return keys

    async def get(self, session, url):
        try:
            response = await session.get(url, ssl=settings.ENABLE_SSL)
        except aiohttp.client_exceptions.ClientConnectorError:
            # Some error occurred when connecting, timeout or domain
            # not resolvable.
            self.logger.error(
                "Unable to connect load JWKS from %s", self.server)
            return
        if response.status != 200:
            self.logger.error(
                "Non-200 response from server (%s) GET %s",
                response.status, self.url)
            return
        try:
            return json.loads(await response.text())
        except ValueError:
            self.logger.error(
                "Parsing error: %s", self.url
            )
            return
