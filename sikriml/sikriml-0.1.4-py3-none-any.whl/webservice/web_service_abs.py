from abc import ABC, abstractmethod

from azureml.core import Environment, Workspace
from azureml.core.compute import ComputeTarget
from azureml.core.model import InferenceConfig, Model
from azureml.core.webservice import Webservice
from azureml.core.webservice.aci import WebserviceDeploymentConfiguration

from .web_service_config import WebserviceConfiguration

HEALTHY_STATE = "healthy"


class WebserviceAbstract(ABC):
    def __init__(
        self, workspace: Workspace, service_config: WebserviceConfiguration
    ) -> None:
        self._workspace = workspace
        self.__config = service_config

    @abstractmethod
    def get_deploy_config(self) -> WebserviceDeploymentConfiguration:
        pass

    def get_deployment_target(self) -> ComputeTarget:
        return None

    def deploy(self) -> Webservice:
        webservices = self._workspace.webservices.keys()
        if self.__config.service_name not in webservices:
            service = self.__create_service()
        else:
            service = self.__update_service()

        service.wait_for_deployment(show_output=True)
        self.__validate_service_state(service)
        return service

    def __create_service(self) -> Webservice:
        service = Model.deploy(
            self._workspace,
            self.__config.service_name,
            self.__get_models(),
            self.__get_inference_config(),
            self.get_deploy_config(),
            self.get_deployment_target(),
        )
        return service

    def __get_models(self):
        return [
            self._workspace.models.get(name)
            for name in self.__config.model_names
        ]

    def __get_inference_config(self) -> InferenceConfig:
        environment = Environment.get(
            self._workspace, self.__config.environment_name
        )
        return InferenceConfig(
            environment=environment,
            source_directory=self.__config.source_directory,
            entry_script=self.__config.entry_script,
        )

    def __update_service(self) -> Webservice:
        service = Webservice(
            name=self.__config.service_name,
            workspace=self._workspace,
        )
        service.update(
            models=self.__get_models(),
            inference_config=self.__get_inference_config(),
        )
        return service

    def __validate_service_state(self, service: Webservice) -> None:
        if service.state.lower() != HEALTHY_STATE:
            raise Exception("Status is " + service.state)
