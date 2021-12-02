from enum import Enum
from typing import Optional

from dnastack.constants import default_auth


class ServiceType(Enum):
    DATACONNECT = "dataconnect"
    COLLECTIONS = "collections"
    WES = "wes"

    @staticmethod
    def from_string(name: str):
        for service_type in list(ServiceType):
            if name == service_type.value:
                return service_type
        raise Exception(f"Could not find service type of name [{name}]")


class BaseServiceClient:
    def __init__(
        self,
        parent,
        service_url: str,
        service_type: ServiceType,
        auth_params: dict = default_auth,
    ):
        self.parent = parent
        self.service_url = service_url
        self.service_type = service_type
        self.auth_params = auth_params

    def get_wallet_url(self) -> Optional[str]:
        try:
            return self.auth_params["url"]
        except Exception as e:
            raise Exception(f"Unable to get Wallet url for service: {e}")

    def get_client_oauth_token(self) -> Optional[dict]:
        try:
            return self.parent.auth.oauth.get(self.auth_params["url"])
        except Exception as e:
            raise Exception(f"Unable to get OAuth token for service: {e}")

    def set_refresh_token(self, token: str) -> None:
        try:
            if self.parent.auth.oauth.get(self.get_wallet_url()) is None:
                self.parent.auth.oauth[self.get_wallet_url()] = {}
            self.parent.auth.oauth[self.auth_params["url"]]["refresh_token"] = token
        except Exception as e:
            raise Exception(f"Unable to set OAuth refresh token for service: {e}")
