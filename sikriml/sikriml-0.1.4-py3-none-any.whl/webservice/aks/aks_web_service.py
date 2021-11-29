from azureml.core import Workspace
from azureml.core.compute import AksCompute, ComputeTarget
from azureml.core.webservice.aks import AksServiceDeploymentConfiguration
from azureml.exceptions import ComputeTargetException
from sikriml.webservice import WebserviceAbstract

from .aks_deploy_config_abs import AksDeploymentConfigurationAbstract


class AksWebService(WebserviceAbstract):
    def __init__(
        self,
        workspace: Workspace,
        deploy_config: AksDeploymentConfigurationAbstract,
    ):
        WebserviceAbstract.__init__(self, workspace, deploy_config.base_config)
        self.__deploy_config = deploy_config
        print(self.__deploy_config.base_config.model_names)

    def get_deploy_config(self) -> AksServiceDeploymentConfiguration:
        return self.__deploy_config

    def __attach_compute_target(self) -> ComputeTarget:
        attach_config = AksCompute.attach_configuration(
            resource_group=self._workspace.resource_group,
            cluster_name=self.__deploy_config.base_config.cluster_name,
            cluster_purpose=self.__deploy_config.base_config.cluster_purpose,
        )
        aks_target = ComputeTarget.attach(
            self._workspace,
            self.__deploy_config.base_config.compute_target_name,
            attach_config,
        )
        # Wait for the attach process to complete
        aks_target.wait_for_completion(show_output=True)
        return aks_target

    def get_deployment_target(self) -> ComputeTarget:
        try:
            return ComputeTarget(
                self._workspace,
                self.__deploy_config.base_config.compute_target_name,
            )
        except ComputeTargetException:
            return self.__attach_compute_target()
