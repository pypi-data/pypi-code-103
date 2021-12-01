import pandas as pd
from dagster import DagsterType, dagster_type_loader
from sklearn.base import BaseEstimator

from qdk.utils.typing import is_dataframe, is_mlflow_run, is_model, is_series


@dagster_type_loader(config_schema={})
def load_empty_model(_context, value):  # pylint: disable=unused-argument
    return BaseEstimator()


@dagster_type_loader(config_schema={})
def load_empty_series(_context, value):  # pylint: disable=unused-argument
    return pd.Series()


DataFrameType = DagsterType(
    name="DataFrameType",
    type_check_fn=lambda _, value: is_dataframe(value),
    description="Can represent either a pandas or dask dataframe.",
)
SeriesType = DagsterType(
    name="SeriesType",
    type_check_fn=lambda _, value: is_series(value),
    description="Can represent either a pandas or dask series.",
    loader=load_empty_series,
)
ModelType = DagsterType(
    name="ModelType",
    type_check_fn=lambda _, value: is_model(value),
    description="Generic typing for machine learning models.",
    loader=load_empty_model,
)
MLFlowRunType = DagsterType(
    name="MLFlowRunType",
    type_check_fn=lambda _, value: is_mlflow_run(value),
    description="A type that represents a qdk.MLFlowRun class.",
)
