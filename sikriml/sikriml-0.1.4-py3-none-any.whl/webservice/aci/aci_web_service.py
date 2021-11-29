from azureml.core import Workspace
from azureml.core.webservice.aci import AciServiceDeploymentConfiguration
from sikriml.webservice.web_service_abs import WebserviceAbstract

from .aci_deploy_config_abs import AciDeploymentConfigurationAbstract


class AciWebservice(WebserviceAbstract):
    def __init__(
        self,
        workspace: Workspace,
        deploy_config: AciDeploymentConfigurationAbstract,
    ):
        WebserviceAbstract.__init__(self, workspace, deploy_config.base_config)
        self.__config = deploy_config

    def get_deploy_config(self) -> AciServiceDeploymentConfiguration:
        return self.__config
