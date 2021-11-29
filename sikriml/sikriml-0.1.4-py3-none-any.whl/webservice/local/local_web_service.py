from azureml.core import Workspace
from azureml.core.webservice.local import (
    LocalWebserviceDeploymentConfiguration,
)
from sikriml.webservice.web_service_abs import WebserviceAbstract

from .local_deploy_config_abs import LocalDeploymentConfigurationAbstract


class LocalWebservice(WebserviceAbstract):
    def __init__(
        self,
        workspace: Workspace,
        deploy_config: LocalDeploymentConfigurationAbstract,
    ):
        WebserviceAbstract.__init__(self, workspace, deploy_config.base_config)
        self.__config = deploy_config

    def get_deploy_config(self) -> LocalWebserviceDeploymentConfiguration:
        return self.__config
