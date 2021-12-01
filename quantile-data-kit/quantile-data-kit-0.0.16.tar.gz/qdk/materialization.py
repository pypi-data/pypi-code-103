from abc import ABC, abstractstaticmethod
from typing import Any, Dict, List, Optional

from dagster import AssetMaterialization, EventMetadata
from dask.dataframe import DataFrame as DaskDataFrame
from pandas import DataFrame

from .mlflow import MLFlowRun
from .utils.typing import is_dask_dataframe, is_mlflow_run, is_pandas_dataframe


def list_to_string(list: List[Any]) -> str:
    return f"[{', '.join(list)}]"


class MetaData(ABC):
    @abstractstaticmethod
    def metadata(object: Any) -> Dict[str, Any]:
        pass


class PandasDataFrameMetaData(MetaData):
    @staticmethod
    def create_metadata(object: DataFrame) -> Dict[str, Any]:
        if not is_pandas_dataframe(object):
            raise ValueError("Object is not a pandas dataframe")

        return {
            "columns": list_to_string(object.columns),
            "dask": 0,
            "length": len(object),
            "head": EventMetadata.md(object.head().to_markdown()),
            "tail": EventMetadata.md(object.tail().to_markdown()),
        }


class DaskDataFrameMetaData(MetaData):
    @staticmethod
    def create_metadata(object: DaskDataFrame) -> Dict[str, Any]:
        if not is_dask_dataframe(object):
            raise ValueError("Object is not a dask dataframe")

        return {
            "columns": list_to_string(object.columns), 
            "dask": 1,
        }


class MLFlowRunMetaData(MetaData):
    @staticmethod
    def create_metadata(object: MLFlowRun) -> Dict[str, Any]:
        if not is_mlflow_run(object):
            raise ValueError("Object is not a mlflow run")

        return {
            "run_id": object.run_id,
            "model_flavors": list_to_string(object.model_flavors),
            "run_url": EventMetadata.url(object.run_url),
            "run_url_local": EventMetadata.url(object.run_url_local),
            "input_schema": EventMetadata.md(object.input_schema.to_markdown()),
            "output_schema": EventMetadata.md(object.output_schema.to_markdown()),
        }


class Materializer:
    def __init__(self, asset_key: str, object: Any):
        self.asset_key = asset_key
        self.object = object

        if is_pandas_dataframe(object):
            self.metadata = PandasDataFrameMetaData.create_metadata(object)
        elif is_dask_dataframe(object):
            self.metadata = DaskDataFrameMetaData.create_metadata(object)
        elif is_mlflow_run(object):
            self.metadata = MLFlowRunMetaData.create_metadata(object)
        else:
            self.metadata = {}

    def materialize(self) -> Optional[AssetMaterialization]:
        if self.metadata:
            return AssetMaterialization(
                asset_key=self.asset_key,
                metadata=self.metadata,
            )
