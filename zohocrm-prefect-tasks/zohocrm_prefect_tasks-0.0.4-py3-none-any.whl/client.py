from zcrmsdk.src.com.zoho.crm.api.user_signature import UserSignature
from zcrmsdk.src.com.zoho.crm.api.dc import USDataCenter, EUDataCenter, INDataCenter, CNDataCenter, AUDataCenter
from zcrmsdk.src.com.zoho.api.authenticator.store import FileStore
from zcrmsdk.src.com.zoho.api.logger import Logger
from zcrmsdk.src.com.zoho.crm.api.initializer import Initializer
from zcrmsdk.src.com.zoho.api.authenticator.oauth_token import OAuthToken, TokenType
from zcrmsdk.src.com.zoho.crm.api.sdk_config import SDKConfig


class ApiClient:
    def __init__(self, log_path: str = None, store_path: str = None, resource_path: str = None, email: str = None,
                 env: str = "USDataCenter", client_id: str = None, client_secret: str = None,
                 refresh_token: str = None):
        if log_path is None:
            raise ValueError("A log path must be provided.")

        if store_path is None:
            raise ValueError("A store path must be provided.")

        if resource_path is None:
            raise ValueError("A resource path must be provided.")

        if email is None:
            raise ValueError("An email must be provided.")

        if client_id is None:
            raise ValueError("A client id must be provided.")

        if client_secret is None:
            raise ValueError("A client secret must be provided")

        if refresh_token is None:
            raise ValueError("A refresh token must be provided")

        self.logger = Logger.get_instance(level=Logger.Levels.INFO, file_path=log_path)

        self.user = UserSignature(email=email)

        if env is "USDatacenter":
            self.environment = USDataCenter.PRODUCTION()
        if env is "EUDatacenter":
            self.environment = EUDataCenter.PRODUCTION()
        if env is "INDatacenter":
            self.environment = INDataCenter.PRODUCTION()
        if env is "CNDatacenter":
            self.environment = CNDataCenter.PRODUCTION()
        if env is "AUDatacenter":
            self.environment = AUDataCenter.PRODUCTION()

        self.token = OAuthToken(client_id=client_id, client_secret=client_secret, token=refresh_token,
                                token_type=TokenType.REFRESH)

        self.store = FileStore(file_path=store_path)

        self.config = SDKConfig(auto_refresh_fields=True, pick_list_validation=False)

        self.resource_path = resource_path

        """
        Call the static initialize method of Initializer class that takes the following arguments
        1 -> UserSignature instance
        2 -> Environment instance
        3 -> Token instance
        4 -> TokenStore instance
        5 -> SDKConfig instance
        6 -> resource_path
        7 -> Logger instance. Default value is None
        8 -> RequestProxy instance. Default value is None
        """
        Initializer.initialize(user=self.user, environment=self.environment, token=self.token, store=self.store,
                               logger=self.logger, sdk_config=self.config, resource_path=self.resource_path)

