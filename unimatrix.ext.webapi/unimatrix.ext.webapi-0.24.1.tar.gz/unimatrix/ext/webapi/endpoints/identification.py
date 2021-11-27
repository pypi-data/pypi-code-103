"""Declares :class:`IdentificationEndpointSet`."""
import ioc
from unimatrix.conf import settings
from unimatrix.ext import jose

from ..resourceendpointset import PublicResourceEndpointSet


class IdentificationEndpointSet(PublicResourceEndpointSet):
    """Exposes endpoints to identify end-users."""
    group_name = "Current user"
    singleton = True

    async def create(self, dto: dict):
        """Use an OpenID token that was issued by a trusted identity provider
        to establish the identity of a user.
        """
        raise NotImplementedError

    async def replace(self, dto: dict):
        """Use an OpenID token that was issued by a trusted identity provider
        to update the identity of an existing user.
        """
        jws = jose.parse(str.encode(dto['token']))
        jws.payload.verify(
            audience=f'https://{self.request.url.netloc}',
            issuers=self.get_issuers()
        )
        self.logger.debug("Verified token from %s", jws.payload.iss)
        await self.verify_signature(jws)
        return dict(jws.payload.claims)

    def get_issuers(self) -> set:
        """Return the issuers that are trusted to created OpenID
        tokens.
        """
        return set(getattr(settings, 'OAUTH2_TRUSTED_IDP', []))

    async def verify_signature(self, jws: jose.JSONWebSignature):
        self.logger.debug("Verified signature from %s", jws.payload.iss)
