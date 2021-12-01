from injector import inject
import logging

from ..providers.identity_provider import JWTIdentityDlcClient
from ..services.abstract_external_service import ExternalService

logger = logging.getLogger(__name__)


class IdentityService(ExternalService):
    """
    Data Lake interface service, for interfacing
    with said interface.

    The JWTIdentityDlcClient should ONLY be responsible
    for authentication and connection pooling. This class
    should be responsible for implementation of high level
    interfacing with the interface component.
    """
    @inject
    def __init__(
        self,
        identity_session: JWTIdentityDlcClient
    ):
        logger.debug('Init IdentityService')
        self.identity_session = identity_session

    def get_visible_organisations(self):
        return self.identity_session.get(
            '/__api_v2/organisations/visible',
            hooks=self._make_hook('No visible organisations.')
        ).json()

    def me(self):
        return self.identity_session.get(
            '/__api_v2/me',
            hooks=self._make_hook('Cannot access identity/me.')
        ).json()