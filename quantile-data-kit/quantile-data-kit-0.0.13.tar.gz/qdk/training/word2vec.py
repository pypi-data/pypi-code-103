import multiprocessing
from typing import Optional, Tuple, Union

import dask.dataframe as dd
import pandas as pd
from dagster import Field, InputDefinition, OutputDefinition
from gensim.models.word2vec import Word2Vec
from qdk.dagster_types import DataFrameType, ModelType
from qdk.training.base import TrainingComponent

from sklearn.base import BaseEstimator


class Word2VecTrainingComponent(TrainingComponent):
    tags = {
        "kind": "word2vec",
    }
    input_defs = [
        InputDefinition(
            "X",
            DataFrameType,
        ),
    ]
    output_defs = [
        OutputDefinition(
            ModelType,
            "model",
        ),
    ]
    config_schema = {
        "token_column": Field(
            str,
            default_value="_tokens_text",
        ),
        "vector_size": Field(
            int,
            default_value=100,
        ),
        "window": Field(
            int,
            default_value=5,
        ),
        "min_count": Field(
            int,
            default_value=5,
        ),
        "negative": Field(
            int,
            default_value=5,
        ),
    }

    @classmethod
    def train(
        cls,
        X: Union[pd.DataFrame, dd.DataFrame],
        token_column: str = "_tokens_text",
        vector_size: int = 100,
        window: int = 5,
        min_count: int = 5,
        negative: int = 5
    ) -> Word2Vec:
        # Train the Word2Vec model
        word2vec_model = Word2Vec(
            sentences=X[token_column],
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            negative=5,
            workers=multiprocessing.cpu_count(),
        )

        return word2vec_model
