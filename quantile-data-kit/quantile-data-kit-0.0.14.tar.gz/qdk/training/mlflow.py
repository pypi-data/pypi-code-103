import pandas as pd
import dask.dataframe as dd
from dagster import Field, OutputDefinition, Permissive
from qdk.dagster_types import MLFlowRunType
from qdk.training.base import TrainingComponent
from qdk.mlflow import MLFlowRun
from typing import Any, Dict, Union
from sklearn.base import BaseEstimator
from mlflow import set_experiment, autolog, start_run, xgboost, sklearn


class MLFlowTrainingComponent(TrainingComponent):
    # required_resource_keys = {"mlflow"}
    output_defs = [OutputDefinition(MLFlowRunType, "mlflow_run")]
    config_schema = {
        "experiment_name": Field(
            str,
            default_value="default",
            description="The mlflow experiment name, if it doesn't exists it will be created.",
        )
    }

    @classmethod
    def train(
        cls,
        X: Union[pd.DataFrame, dd.DataFrame],
        y: Union[pd.Series, dd.Series],
        model: BaseEstimator,
        experiment_name: str = "default",
    ):
        set_experiment(experiment_name)
        autolog(disable=False)

        with start_run() as run:
            model.fit(X, y)

        autolog(disable=True)
        return MLFlowRun(run)
