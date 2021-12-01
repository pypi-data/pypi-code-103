from featurestore.core.schema import Column, Schema

from .base_job import BaseJob


class ExtractSchemaJob(BaseJob):
    def _response_method(self, job_id):
        response = self._stub.GetExtractSchemaJobOutput(job_id)
        return Schema(
            [Column(field.name, field.data_type) for field in response.schema]
        )
