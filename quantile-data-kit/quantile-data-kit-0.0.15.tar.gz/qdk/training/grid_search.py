from dagster.config.field import Field
import pandas as pd
import dask.dataframe as dd
from dagster import InputDefinition, Permissive
from qdk.dagster_types import DataFrameType, SeriesType
from qdk.training.base import TrainingComponent
from typing import Any, Dict, Union
from sklearn.base import BaseEstimator

# from dask_ml.model_selection import RandomizedSearchCV
from sklearn.model_selection import RandomizedSearchCV
import mlflow


class GridSearchTrainingComponent(TrainingComponent):
    config_schema = {
        "params": Field(
            Permissive({}),
            description="The grid search parameters to provide to the model",
        ),
        "scoring": Field(
            str,
            description="The scoring function to use for the grid search",
        ),
        "n_iter": Field(
            int,
            default_value=10,
            description="The number of iterations to run the grid search",
        ),
    }

    @classmethod
    def train(
        cls,
        X: Union[pd.DataFrame, dd.DataFrame],
        y: Union[pd.Series, dd.Series],
        model: BaseEstimator,
        params: Dict[str, Any],
        scoring: str,
        n_iter: int = 10,
    ) -> BaseEstimator:
        # Create the search object
        search = RandomizedSearchCV(
            estimator=model,
            param_distributions=params,
            n_iter=n_iter,
            random_state=0,
            scoring=scoring,
        )

        mlflow.sklearn.autolog()

        # Fit the search on the data
        with mlflow.start_run() as run:
            search.fit(X, y)

        return search
