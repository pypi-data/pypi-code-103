from typing import Optional, List
from urllib.parse import urlencode
from .output.dataset_version_output import DatasetVersionOutput
from .output.paged_response import PagedResponse

from vectice.api.dataset import DatasetApi
from vectice.entity import DatasetVersion
from .output.property_output import EntityPropertyOutput
from .json_object import JsonObject
from .Page import Page


class DatasetVersionApi(DatasetApi):
    def __init__(self, project_token: str, dataset_id: int, _token: Optional[str] = None):
        super().__init__(project_token=project_token, _token=_token)
        self._dataset_id = dataset_id
        self._dataset_version_path = super().api_base_path + "/" + str(dataset_id) + "/version"

    @property
    def dataset_id(self) -> int:
        return self._dataset_id

    @property
    def api_base_path(self) -> str:
        return self._dataset_version_path

    def list_dataset_versions(self, page_index=Page.index, page_size=Page.size) -> PagedResponse[DatasetVersionOutput]:
        queries = {"index": page_index, "size": page_size}
        dataset_versions = self._get(self.api_base_path + "?" + urlencode(queries))
        return PagedResponse(
            item_cls=DatasetVersionOutput,
            total=dataset_versions["total"],
            page=dataset_versions["page"],
            items=dataset_versions["items"],
        )

    def create_dataset_version(self, dataset_version: JsonObject) -> DatasetVersion:
        return DatasetVersion(self._post(self.api_base_path, dataset_version))

    def update_dataset_version(self, dataset_id: int, dataset_version) -> DatasetVersion:
        return DatasetVersion(self._put(self.api_base_path + "/" + str(dataset_id), dataset_version))

    def create_dataset_version_properties(self, dataset_version_id: int, properties: List[dict]):
        if len(properties) >= 1:
            for prop in properties:
                DatasetVersion(self._post(self.api_base_path + f"/{dataset_version_id}/entityProperty/", prop))

    def update_dataset_version_property(
        self, dataset_version_id: int, property_id: int, dataset_version_properties: JsonObject
    ):
        return DatasetVersion(
            self._put(
                self.api_base_path + f"/{dataset_version_id}/entityProperty/{property_id}", dataset_version_properties
            )
        )

    def list_dataset_version_properties(
        self, dataset_version_id: int, page_index=Page.index, page_size=Page.size
    ) -> PagedResponse[EntityPropertyOutput]:
        queries = {"index": page_index, "size": page_size}
        model_version_properties = self._get(
            self.api_base_path + f"/{dataset_version_id}/entityProperty?" + urlencode(queries)
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
