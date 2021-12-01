from typing import Optional
from urllib.parse import urlencode
from .output.model_version_output import ModelVersionOutput
from .output.metric_output import EntityMetricOutput
from .output.property_output import EntityPropertyOutput
from .output.paged_response import PagedResponse
from .json_object import JsonObject
from .model import ModelApi
from vectice.entity import ModelVersion
from .Page import Page


class ModelVersionApi(ModelApi):
    def __init__(self, project_token: str, model_id: int, _token: Optional[str] = None):
        super().__init__(project_token=project_token, _token=_token)
        self._model_id = model_id
        self._model_version_path = super().api_base_path + "/" + str(model_id) + "/version"

    @property
    def model_id(self) -> int:
        return self._model_id

    @property
    def api_base_path(self) -> str:
        return self._model_version_path

    def list_model_versions(self, page_index=Page.index, page_size=Page.size) -> PagedResponse[ModelVersionOutput]:
        queries = {"index": page_index, "size": page_size}
        model_versions = self._get(self.api_base_path + "?" + urlencode(queries))
        return PagedResponse(
            item_cls=ModelVersionOutput,
            total=model_versions["total"],
            page=model_versions["page"],
            items=model_versions["items"],
        )

    def create_model_version(self, model_version: JsonObject) -> ModelVersion:
        if model_version.get("status") is None:
            raise ValueError('"status" must be provided in model_version.')
        return ModelVersion(self._post(self.api_base_path, model_version))

    def update_model_version(self, model_id: int, model_version: JsonObject) -> ModelVersion:
        return ModelVersion(self._put(self.api_base_path + "/" + str(model_id), model_version))

    def list_model_version_metrics(
        self, model_version_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[EntityMetricOutput]:
        queries = {"index": page_index, "size": page_size}
        model_version_metrics = self._get(
            self.api_base_path + f"/{model_version_id}/entityMetric?" + urlencode(queries)
        )
        metrics = [EntityMetricOutput.from_dict(metric).as_dict() for metric in model_version_metrics["items"]]
        return PagedResponse(
            item_cls=EntityMetricOutput,
            total=model_version_metrics["total"],
            page=model_version_metrics["page"],
            items=metrics,
        )

    def list_model_version_properties(
        self, model_version_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[EntityPropertyOutput]:
        queries = {"index": page_index, "size": page_size}
        model_version_properties = self._get(
            self.api_base_path + f"/{model_version_id}/entityProperty?" + urlencode(queries)
        )
        properties = [
            EntityPropertyOutput.from_dict(property).as_dict() for property in model_version_properties["items"]
        ]
        return PagedResponse(
            item_cls=EntityPropertyOutput,
            total=model_version_properties["total"],
            page=model_version_properties["page"],
            items=properties,
        )
