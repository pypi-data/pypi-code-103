"""Declares :class:`HTTPAuthenticationService`."""
import asyncio
import logging

from unimatrix.ext import crypto
from unimatrix.ext import jose

from ...exceptions import TrustIssues
from ...exceptions import UntrustedIssuer
from ...exceptions import UpstreamServiceNotAvailable
from ..ihttpauthenticationservice import IHTTPAuthenticationService


class HTTPAuthenticationService(IHTTPAuthenticationService):
    logger = logging.getLogger('uvicorn')

    async def resolve(self,
        bearer: bytes,
        audience: set = None,
        issuers: set = None,
        scope: set = None,
        policy = None
    ):
        """Decode JWT `bearer` and return the principal described by the
        claimset.

        Args:
            bearer (str): the bearer token as received by the ``Authorization``
                header.
            audience (set): a list of string indicating the audiences that
                are valid for this bearer token. If `audience` is ``None`` or
                empty, then no validation of the ``aud`` claim is performed.
            issuers (set): the list of issuers that should be trusted.
            scope (set): the required scope.
            policy: the policy to apply when verifying the signature.
        """
        # Get the header from the JWS. If the header does not contain the
        # `kid` claim, then we assume that the token was issued using our
        # own secret key (HS256 or similar). A JWS that specifies the `kid`
        # claim in its header, was signed by a third party. This key is
        # retrieved from the key registry and matched against the policy
        # specified by the invocation parameters.
        jws = jose.parse(bearer)

        # If there is a `kid` claim on the JWS, then there MUST be a
        # policy to determine if we trust the key.
        if jws.header.kid is not None and not policy: # pragma: no cover
            raise ValueError(
                "The policy argument is required for identified keys."
            )
        await self.verify(issuers, jws.header.kid, jws, policy)
        jwt = jws.payload
        jwt.verify(
            audience=audience or None,
            issuers=issuers or None,
            scope=scope or None,
            required={"iss", "aud", "iat", "exp", "sub"}
        )

        return jwt.claims

    async def verify(self, issuers, kid, jws, policy):
        """Verify the digital signature of the JWS."""
        issuers = issuers or []
        if jws.payload.iss not in issuers:
            raise UntrustedIssuer(jws.payload.iss, issuers)
        try:
            key = (await self.get_public_key(kid, jws.payload))\
                if kid else\
                crypto.get_secret_key()
        except LookupError:
            raise TrustIssues
        await jws.verify(key)
        if policy is not None:
            await policy.enforce(key)

    async def get_public_key(self, kid, jwt, attempts=0, max_attempts=5):
        """Returns the public key identified by `kid`."""
        try:
            return crypto.trust.get(kid)
        except LookupError:
            if not jwt.iss or (jwt.iss == 'self'):
                raise
            self.logger.debug(
                "Public key unknown, trying lookup (kid: %s, issuer: %s)",
                kid, jwt.iss
            )
            if attempts >= max_attempts:
                self.logger.error(
                    "Could not retrieve key after %s attempts "
                    "(kid: %s, issuer: %s)",
                    attempts, kid, jwt.iss
                )
                raise UpstreamServiceNotAvailable
            if attempts > 0:
                self.logger.warning("Retrying JWKS lookup for %s", jwt.iss)
            await crypto.trust.jwks(jwt.iss,
                ['oauth2.sts'],
                {'oauth2/sts': jwt.iss}
            )
            self.logger.debug("Retrieved public key (kid: %s, issuer: %s)",
                kid, jwt.iss)
            return await self.get_public_key(kid, jwt, attempts+1)
