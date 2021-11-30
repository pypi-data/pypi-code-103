from dataclasses import dataclass
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from common.api.dtos.cloud_provider_dto import CloudProviderDTO


@dataclass
class ConnectionTestDTO(DataClassJsonMixin):
    """
    ---
    properties:
        account_id:
            type: string
            description: 
                The cloud account ID, must match the identifier provided
                by the cloud service provider.
        connection_test_passed:
            type: boolean
            description: Set to 'true' if the test was successful.
        authentication_failure_reason:
            type: string
            description:
                If connection_test_passed is false, this field will specify the reason why the connection test failed.
    """
    connection_test_passed: bool
    account_id: Optional[str] = None
    authentication_failure_reason: Optional[str] = None


@dataclass
class ConnectivityTestRequestDTO(DataClassJsonMixin):
    """
    ---
    properties:
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
        tenant_id:
            type: string
            description:
                For Azure, specifies the tenant ID we're connect to.
        client_id:
            type: string
            description:
                For Azure, specifies the client ID we're connect to.
        client_secret:
            type: string
            description:
                For Azure, specifies the client secret to use when connecting.
        client_email:
            type: string
            description:
                For GCP, specifies the email address used to identify the service address Cloudrail is connecting through.
    """
    cloud_provider: CloudProviderDTO
    cloud_account_id: Optional[str] = None
    # Azure
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    # GCP
    client_email: Optional[str] = None
    token_uri: Optional[str] = None
    private_key: Optional[str] = None
