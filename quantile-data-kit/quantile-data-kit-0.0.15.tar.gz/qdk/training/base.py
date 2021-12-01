from typing import Optional, Tuple, Union

import dask.dataframe as dd
import pandas as pd
from dagster import InputDefinition, Nothing
from dagster import Optional as DagsterOptional
from dagster import OutputDefinition
from qdk.base import BaseComponent
from qdk.dagster_types import DataFrameType, ModelType, SeriesType

from sklearn.base import BaseEstimator


class TrainingComponent(BaseComponent):
    compute_function = "train"
    tags = {
        "kind": "training",
    }
    input_defs = [
        InputDefinition(
            "X",
            DataFrameType,
        ),
        InputDefinition(
            "y",
            DagsterOptional[SeriesType],
        ),
        InputDefinition(
            "model",
            DagsterOptional[ModelType],
        ),
    ]
    output_defs = [
        OutputDefinition(
            ModelType,
            "model",
        ),
        OutputDefinition(
            DataFrameType,
            "data",
            is_required=False,
        ),
    ]

    @classmethod
    def train(
        cls,
        X: Union[pd.DataFrame, dd.DataFrame],
        model: Optional[BaseEstimator] = None,
        y: Optional[Union[pd.Series, dd.Series]] = None,
    ) -> Tuple[BaseEstimator, Optional[Union[pd.DataFrame, dd.DataFrame]]]:
        raise NotImplementedError(
            'Make sure you added a "train" function to the component'
        )
