from typing import Callable

from ai_core_sdk.exception import AIAPIAuthenticatorException
from ai_core_sdk.helpers import Authenticator
from ai_core_sdk.resource_clients import AIAPIV2Client, ArtifactClient, ConfigurationClient, DeploymentClient, \
    ExecutableClient, ExecutionClient, RestClient, ScenarioClient
from ai_core_sdk.resource_clients.applications_client import ApplicationsClient
from ai_core_sdk.resource_clients.docker_registry_secrets_client import DockerRegistrySecretsClient
from ai_core_sdk.resource_clients.metrics_client import MetricsCoreClient
from ai_core_sdk.resource_clients.object_store_secrets_client import ObjectStoreSecretsClient
from ai_core_sdk.resource_clients.kpi_client import KpiClient
from ai_core_sdk.resource_clients.repositories_client import RepositoriesClient
from ai_core_sdk.resource_clients.resource_groups_client import ResourceGroupsClient


class AICoreV2Client:
    """The AICoreV2Client is the class implemented to interact with the AI Core endpoints. The user can use its
    attributes corresponding to the resources, for interacting with endpoints related to that resource. (i.e.,
    aicoreclient.scenario)

    :param base_url: Base URL of the AI Core. Should include the base path as well. (i.e., "<base_url>/lm/scenarios"
        should work)
    :type base_url: str
    :param auth_url: URL of the authorization endpoint. Should be the full URL (including /oauth/token), defaults to
        None
    :type auth_url: str, optional
    :param client_id: client id to be used for authorization, defaults to None
    :type client_id: str, optional
    :param client_secret: client secret to be used for authorization, defaults to None
    :type client_secret: str, optional
    :param token_creator: the function which returns the Bearer token, when called. Either this, or
        auth_url & client_id & client_secret should be specified, defaults to None
    :type token_creator: Callable[[], str], optional
    :param resource_group: The default resource group which will be used while sending the requests to the server. If
        not set, the resource_group should be specified with every request to the server, defaults to None
    :type resource_group: str, optional
    """
    def __init__(self, base_url: str, auth_url: str = None, client_id: str = None, client_secret: str = None,
                 token_creator: Callable[[], str] = None, resource_group: str = None):
        self.base_url: str = base_url
        ai_api_base_url = f'{base_url}/lm'
        if not token_creator:
            if not (auth_url and client_id and client_secret):
                raise AIAPIAuthenticatorException(
                    'Either token_creator or auth_url & client_id & client_secret should be provided')
            token_creator = Authenticator(auth_url=auth_url, client_id=client_id, client_secret=client_secret).get_token
        ai_api_v2_client = AIAPIV2Client(base_url=ai_api_base_url, auth_url=auth_url, token_creator=token_creator,
                                         resource_group=resource_group)
        self.rest_client: RestClient = RestClient(base_url=base_url, get_token=token_creator, resource_group=resource_group)
        self.artifact: ArtifactClient = ai_api_v2_client.artifact
        self.configuration: ConfigurationClient = ai_api_v2_client.configuration
        self.deployment: DeploymentClient = ai_api_v2_client.deployment
        self.executable: ExecutableClient = ai_api_v2_client.executable
        self.execution: ExecutionClient = ai_api_v2_client.execution
        self.metrics: MetricsCoreClient = MetricsCoreClient(rest_client=ai_api_v2_client.rest_client)
        self.scenario: ScenarioClient = ai_api_v2_client.scenario
        self.docker_registry_secrets: DockerRegistrySecretsClient = DockerRegistrySecretsClient(rest_client=self.rest_client)
        self.applications: ApplicationsClient = ApplicationsClient(rest_client=self.rest_client)
        self.object_store_secrets: ObjectStoreSecretsClient = ObjectStoreSecretsClient(rest_client=self.rest_client)
        self.kpis: KpiClient = KpiClient(rest_client=self.rest_client)
        self.repositories: RepositoriesClient = RepositoriesClient(rest_client=self.rest_client)
        self.resource_groups: ResourceGroupsClient = ResourceGroupsClient(rest_client=self.rest_client)
