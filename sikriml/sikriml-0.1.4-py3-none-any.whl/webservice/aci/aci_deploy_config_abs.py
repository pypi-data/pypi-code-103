from abc import ABC, abstractclassmethod

from azureml.core.webservice.aci import AciServiceDeploymentConfiguration
from sikriml.webservice import WebserviceConfiguration


class AciDeploymentConfigurationAbstract(
    AciServiceDeploymentConfiguration, ABC
):
    base_config: WebserviceConfiguration

    def __init__(
        self,
        cpu_cores=None,
        memory_gb=None,
        tags=None,
        properties=None,
        description=None,
        location=None,
        auth_enabled=None,
        ssl_enabled=None,
        enable_app_insights=None,
        ssl_cert_pem_file=None,
        ssl_key_pem_file=None,
        ssl_cname=None,
        dns_name_label=None,
        primary_key=None,
        secondary_key=None,
        collect_model_data=None,
        cmk_vault_base_url=None,
        cmk_key_name=None,
        cmk_key_version=None,
        vnet_name=None,
        subnet_name=None,
    ):
        AciServiceDeploymentConfiguration.__init__(
            self,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            tags=tags,
            properties=properties,
            description=description,
            location=location,
            auth_enabled=auth_enabled,
            ssl_enabled=ssl_enabled,
            enable_app_insights=enable_app_insights,
            ssl_cert_pem_file=ssl_cert_pem_file,
            ssl_key_pem_file=ssl_key_pem_file,
            ssl_cname=ssl_cname,
            dns_name_label=dns_name_label,
            primary_key=primary_key,
            secondary_key=secondary_key,
            collect_model_data=collect_model_data,
            cmk_vault_base_url=cmk_vault_base_url,
            cmk_key_name=cmk_key_name,
            cmk_key_version=cmk_key_version,
            vnet_name=vnet_name,
            subnet_name=subnet_name,
        )
        self.base_config = self.get_base_config()

    @abstractclassmethod
    def get_base_config(self) -> WebserviceConfiguration:
        pass
