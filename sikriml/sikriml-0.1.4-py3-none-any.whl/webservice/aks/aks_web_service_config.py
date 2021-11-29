from typing import List

from azureml.core.compute import AksCompute
from sikriml.webservice import WebserviceConfiguration


class AksWebserviceConfiguration(WebserviceConfiguration):
    def __init__(
        self,
        environment_name: str,
        service_name: str,
        source_directory: str,
        entry_script: str,
        cluster_name: str,
        compute_target_name: str,
        cluster_purpose: AksCompute.ClusterPurpose,
        model_names: List[str] = [],
    ):
        WebserviceConfiguration.__init__(
            self,
            environment_name,
            service_name,
            source_directory,
            entry_script,
            model_names,
        )
        self.cluster_name = cluster_name
        self.compute_target_name = compute_target_name
        self.cluster_purpose = cluster_purpose
