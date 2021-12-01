import pandas as pd
import dask.dataframe as dd
from dagster import InputDefinition
from qdk.dagster_types import DataFrameType, SeriesType
from qdk.training.base import TrainingComponent
from typing import Union
from sklearn.base import BaseEstimator


class SklearnComponent(TrainingComponent):
    input_defs = [
        InputDefinition("X", DataFrameType),
        InputDefinition("y", SeriesType),
        InputDefinition("model", BaseEstimator),
    ]
    required_resource_keys = {"mlflow"}

    @classmethod
    def train(
        cls,
        X: Union[pd.DataFrame, dd.DataFrame],
        y: Union[pd.Series, dd.Series],
        model: BaseEstimator,
    ):
        return model.fit(X, y)
