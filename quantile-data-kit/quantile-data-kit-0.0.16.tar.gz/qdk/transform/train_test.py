import pandas as pd
import yake
import dask.dataframe as dd

from dagster import InputDefinition, OutputDefinition, Field
from typing import Dict, List, Tuple, Union
from qdk.transform.base import TransformComponent
from qdk.dagster_types import DataFrameType, SeriesType
from dask_ml.model_selection import train_test_split


class TrainTestComponent(TransformComponent):
    input_defs = [InputDefinition("df", DataFrameType)]
    output_defs = [
        OutputDefinition(DataFrameType, "X_train"),
        OutputDefinition(DataFrameType, "X_test"),
        OutputDefinition(SeriesType, "y_train"),
        OutputDefinition(SeriesType, "y_test"),
    ]
    config_schema = {
        "target_column": Field(
            str,
            is_required=True,
            description="The column to use as target",
        ),
        "test_size": Field(
            float,
            default_value=0.2,
            description="The proportion of the dataset to include in the test split",
        ),
        "shuffle": Field(
            bool,
            default_value=True,
            description="Whether or not to shuffle the data before splitting",
        ),
    }

    @staticmethod
    def _extract_keywords(
        text, extractor: yake.KeywordExtractor
    ) -> List[Tuple[str, float]]:
        """Extracts keywords from a string using a yake KeywordExtractor instance.

        Args:
            text (str): The text you want to extract the keywords from.
            extractor (yake.KeywordExtractor): The initialized yake keyword extractor.

        Returns:
            List[Tuple[str, float]]: Returns a list with keyword, score tuples. The scores indicates keyword relevence (the lower the better).
        """
        return extractor.extract_keywords(text)

    @classmethod
    def transform(
        cls,
        df: Union[pd.DataFrame, dd.DataFrame],
        target_column: str,
        test_size: float = 0.2,
        shuffle: bool = False,
    ) -> Tuple[
        Union[pd.DataFrame, dd.DataFrame],
        Union[pd.DataFrame, dd.DataFrame],
        Union[pd.Series, dd.Series],
        Union[pd.Series, dd.Series],
    ]:
        """
        Args:
            df (Union[pd.DataFrame, dd.DataFrame]): The dataframe to split.
            target_column (str): The column to use as target.

        Returns:
            Tuple[
                Union[pd.DataFrame, dd.DataFrame],
                Union[pd.DataFrame, dd.DataFrame],
                Union[pd.Series, dd.Series],
                Union[pd.Series, dd.Series]
            ]: Returns a tuple with the train and test dataframes, the train and test target series.
        """
        X = df.drop(target_column, axis=1)
        y = df[target_column]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=shuffle
        )

        return (X_train, X_test, y_train, y_test)
