import ssl
from typing import Dict, Union
from sherpa_client.models import Credentials, RequestJwtTokenProjectAccessMode, BearerToken
from sherpa_client.types import Unset, UNSET, Response
from sherpa_client.client import AuthenticatedClient
import attr


@attr.s(auto_attribs=True)
class SherpaClient(AuthenticatedClient):
    """A Client logged"""

    def login(
        self,
        credentials: Credentials,
        project_filter: Union[Unset, None, str] = UNSET,
        project_access_mode: Union[Unset, None, RequestJwtTokenProjectAccessMode] = UNSET,
        annotate_only: Union[Unset, None, bool] = False,
        login_only: Union[Unset, None, bool] = False,
    ):
        """ """
        from sherpa_client.api.authentication import request_jwt_token

        r: Response[BearerToken] = request_jwt_token.sync_detailed(
            client=self,
            json_body=credentials,
            project_filter=project_filter,
            project_access_mode=project_access_mode,
            annotate_only=annotate_only,
            login_only=login_only,
        )
        if r.is_success:
            self.token = r.parsed.access_token
        else:
            r.raise_for_status()
