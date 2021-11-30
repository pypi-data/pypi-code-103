import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from common.api.dtos.cloud_provider_dto import CloudProviderDTO
from common.input_validator import InputValidator


class AccountStatusDTO(str, Enum):
    CONNECTING = 'connecting'
    INITIAL_ENVIRONMENT_MAPPING = 'initial environment mapping'
    READY = 'ready'
    ERROR = 'error'


@dataclass
class CredentialsDTO(DataClassJsonMixin):
    pass


@dataclass
class AwsCredentialsDTO(CredentialsDTO):
    external_id: Optional[str] = None
    role_name: Optional[str] = None


@dataclass
class AzureCredentialsDTO(CredentialsDTO):
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


@dataclass
class GcpCredentialsDTO(CredentialsDTO):
    client_email: str = None
    token_uri: str = None
    private_key: str = None


@dataclass
class AccountConfigDTO(DataClassJsonMixin):
    """
    ---
    properties:
        id:
            type: string
            description:
                The ID of the cloud account as it is uniquely identified within
                Cloudrail.
        name:
            type: string
            description: The cloud account name as it will appear with Cloudrail.
        cloud_account_id:
            type: string
            description:
                The cloud account ID, must match the identifier provided
                by the cloud service provider.
        created_at:
            type: string
            description: The date when the cloud account was added to Cloudrail.
        last_collected_at:
            type: string
            description:
                The date the last update was made to the cloud account's
                configuration within Cloudrail.
        status:
            type: string
            description: The current status of the cloud account from Cloudrail's perspective.
        drift_detection_enabled:
            type: string
            description: True if automatic drift detection is enabled.
        cloud_provider:
            type: string
            description: The cloud service provider the account is operating within.
            enum:
            - amazon_web_services
            - azure
    """
    name: str
    cloud_account_id: str
    interval_seconds: Optional[int] = None
    credentials: dict = None
    created_at: str = None
    status: AccountStatusDTO = AccountStatusDTO.CONNECTING
    id: str = None
    last_collected_at: str = None
    cloud_provider: CloudProviderDTO = None
    customer_id: str = None
    disable_collect: bool = False
    drift_detection_enabled: bool = True


@dataclass
class AccountConfigAddDTO(DataClassJsonMixin):
    """
    ---
    properties:
        name:
            type: string
            description: The cloud account name as it will appear with Cloudrail.
        cloud_account_id:
            type: string
            description:
                The cloud account ID, must match the identifier provided
                by the cloud service provider.
        cloud_provider:
            type: string
            description: The cloud service provider the account is operating within.
            enum:
            - amazon_web_services
            - azure
        drift_detection_enabled:
            type: boolean
            description:
                True if the regularly check for drift in configuration between
                infrastructure-as-code and the live cloud environment.
        interval_seconds:
            type: integer
            description: How often, in seconds, to pull a new snapshot of the account.
    """
    name: str
    cloud_account_id: str
    cloud_provider: CloudProviderDTO = CloudProviderDTO.AMAZON_WEB_SERVICES
    interval_seconds: Optional[int] = None
    credentials: Optional[CredentialsDTO] = None
    disable_collect: bool = False
    drift_detection_enabled: bool = True

    def __post_init__(self):
        InputValidator.validate_allowed_chars(self.name)
        InputValidator.validate_cloud_account_id(self.cloud_account_id, self.cloud_provider)

    @staticmethod
    def convert_from_json(body):
        account_dict = json.loads(body)
        account_config = AccountConfigAddDTO.from_json(body)
        if credentials := account_dict.get('credentials'):
            if account_config.cloud_provider == CloudProviderDTO.AMAZON_WEB_SERVICES:
                account_config.credentials = AwsCredentialsDTO(credentials.get('external_id'),
                                                               credentials.get('role_name'))
            if account_config.cloud_provider == CloudProviderDTO.AZURE:
                account_config.credentials = AzureCredentialsDTO(credentials.get('tenant_id'),
                                                                 credentials.get('client_id'),
                                                                 credentials.get('client_secret'))
            if account_config.cloud_provider == CloudProviderDTO.GCP:
                account_config.credentials = GcpCredentialsDTO(credentials.get('client_email'),
                                                               credentials.get('token_uri'),
                                                               credentials.get('private_key'))
        return account_config


@dataclass
class AccountConfigUpdateDTO(DataClassJsonMixin):
    """
    ---
    properties:
        name:
            type: string
            description: The cloud account name as it will appear with Cloudrail.
        drift_detection_enabled:
            type: boolean
            description:
                True if the regularly check for drift in configuration between
                infrastructure-as-code and the live cloud environment.
    """
    name: Optional[str] = None
    drift_detection_enabled: Optional[bool] = None

    def __post_init__(self):
        InputValidator.validate_allowed_chars(self.name, allow_none=True)
