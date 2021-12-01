import os
from typing import List

from helios import HeliosBase, HeliosTags
from helios.instrumentation import default_instrumentation_list

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.semconv.resource import ResourceAttributes

SAMPLING_RATIO_RESOURCE_ATTRIBUTE_NAME = 'telemetry.sdk.sampling_ratio'


class Helios(HeliosBase):
    def init_tracer_provider(self) -> TracerProvider:
        if self.resource_tags:
            resource_tags = self.resource_tags.copy()
        else:
            resource_tags = dict()
        resource_tags.update({
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT:
                self.get_deployment_environment(),
            HeliosTags.ACCESS_TOKEN:
                self.api_token,
            ResourceAttributes.SERVICE_NAME:
                self.service_name,
            SAMPLING_RATIO_RESOURCE_ATTRIBUTE_NAME:
                self.sampling_ratio
        })

        return TracerProvider(
            id_generator=self.id_generator,
            sampler=self.get_sampler(),
            resource=Resource.create(resource_tags),
        )

    def get_deployment_environment(self) -> str:

        if self.environment:
            return self.environment

        if self.resource_tags:
            deployment_environment = \
                self.resource_tags.get(
                    ResourceAttributes.DEPLOYMENT_ENVIRONMENT)

            if deployment_environment:
                return deployment_environment

        return os.environ.get('DEPLOYMENT_ENV', '')

    def get_sampler(self):
        if self.custom_sampler:
            return self.custom_sampler

        ratio = self.sampling_ratio or 1.0

        return TraceIdRatioBased(ratio)

    def get_instrumentations(self) -> List[BaseInstrumentor]:
        return default_instrumentation_list
