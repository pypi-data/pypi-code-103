from abc import ABC, abstractclassmethod

from azureml.core.webservice.aks import AksServiceDeploymentConfiguration

from .aks_web_service_config import AksWebserviceConfiguration


class AksDeploymentConfigurationAbstract(
    AksServiceDeploymentConfiguration, ABC
):
    base_config: AksWebserviceConfiguration

    def __init__(
        self,
        autoscale_enabled=None,
        autoscale_min_replicas=None,
        autoscale_max_replicas=None,
        autoscale_refresh_seconds=None,
        autoscale_target_utilization=None,
        collect_model_data=None,
        auth_enabled=None,
        cpu_cores=None,
        memory_gb=None,
        enable_app_insights=None,
        scoring_timeout_ms=None,
        replica_max_concurrent_requests=None,
        max_request_wait_time=None,
        num_replicas=None,
        primary_key=None,
        secondary_key=None,
        tags=None,
        properties=None,
        description=None,
        gpu_cores=None,
        period_seconds=None,
        initial_delay_seconds=None,
        timeout_seconds=None,
        success_threshold=None,
        failure_threshold=None,
        namespace=None,
        token_auth_enabled=None,
        compute_target_name=None,
        cpu_cores_limit=None,
        memory_gb_limit=None,
    ):
        AksServiceDeploymentConfiguration.__init__(
            self,
            autoscale_enabled=autoscale_enabled,
            autoscale_min_replicas=autoscale_min_replicas,
            autoscale_max_replicas=autoscale_max_replicas,
            autoscale_refresh_seconds=autoscale_refresh_seconds,
            autoscale_target_utilization=autoscale_target_utilization,
            collect_model_data=collect_model_data,
            auth_enabled=auth_enabled,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            enable_app_insights=enable_app_insights,
            scoring_timeout_ms=scoring_timeout_ms,
            replica_max_concurrent_requests=replica_max_concurrent_requests,
            max_request_wait_time=max_request_wait_time,
            num_replicas=num_replicas,
            primary_key=primary_key,
            secondary_key=secondary_key,
            tags=tags,
            properties=properties,
            description=description,
            gpu_cores=gpu_cores,
            period_seconds=period_seconds,
            initial_delay_seconds=initial_delay_seconds,
            timeout_seconds=timeout_seconds,
            success_threshold=success_threshold,
            failure_threshold=failure_threshold,
            namespace=namespace,
            token_auth_enabled=token_auth_enabled,
            compute_target_name=compute_target_name,
            cpu_cores_limit=cpu_cores_limit,
            memory_gb_limit=memory_gb_limit,
        )
        self.base_config = self.get_base_config()

    @abstractclassmethod
    def get_base_config(self) -> AksWebserviceConfiguration:
        pass
