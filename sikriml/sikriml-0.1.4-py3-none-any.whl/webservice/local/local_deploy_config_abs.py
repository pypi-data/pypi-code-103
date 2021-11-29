from abc import ABC, abstractclassmethod

from azureml.core.webservice.local import (
    LocalWebserviceDeploymentConfiguration,
)
from sikriml.webservice import WebserviceConfiguration


class LocalDeploymentConfigurationAbstract(
    LocalWebserviceDeploymentConfiguration, ABC
):
    base_config: WebserviceConfiguration

    def __init__(self, port=None):
        LocalWebserviceDeploymentConfiguration.__init__(self, port)
        self.base_config = self.get_base_config()

    @abstractclassmethod
    def get_base_config(self) -> WebserviceConfiguration:
        pass
