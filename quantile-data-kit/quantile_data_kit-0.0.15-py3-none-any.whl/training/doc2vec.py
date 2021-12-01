import multiprocessing
from typing import List, Optional, Tuple, Union

import dask.dataframe as dd
import pandas as pd
from dagster import Field, OutputDefinition
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from pandas.core.frame import DataFrame
from qdk.dagster_types import DataFrameType, ModelType
from qdk.training.word2vec import Word2VecTrainingComponent

from sklearn.base import BaseEstimator


class Doc2VecTrainingComponent(Word2VecTrainingComponent):
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

    @staticmethod
    def tokens_to_tagged_documents(
        token_series: Union[pd.Series, dd.Series],
    ) -> List[TaggedDocument]:
        """Doc2Vec requires TaggedDocuments as input to the model.

        Args:
            token_series (Union[pd.Series, dd.Series]): The input tokens as series.

        Returns:
            List[TaggedDocument]: The tokens encoded as TaggedDocuments
        """
        return [TaggedDocument(doc, [i]) for i, doc in enumerate(token_series)]

    @staticmethod
    def infer_vectors(
        doc2vec_model: Doc2Vec,
        token_series: Union[pd.Series, dd.Series],
    ) -> Union[pd.Series, dd.Series]:
        """Use the Doc2Vec model to infer the embeddings of the token series.

        Args:
            doc2vec_model (Doc2Vec): The Doc2Vec model
            token_series (Union[pd.Series, dd.Series]): The tokens to transform

        Returns:
            Union[pd.Series, dd.Series]: The embeddings
        """
        return token_series.map(doc2vec_model.infer_vector)

    @classmethod
    def train(
        cls,
        X: Union[pd.DataFrame, dd.DataFrame],
        token_column: str = "_tokens_text",
        vector_size: int = 100,
        window: int = 5,
        min_count: int = 5,
        negative: int = 5,
    ) -> Tuple[Doc2Vec, Union[pd.DataFrame, dd.DataFrame]]:
        token_series = X[token_column]

        # Transform the series of tokens to TaggedDocuments
        tagged_documents = cls.tokens_to_tagged_documents(token_series=token_series)

        # Train the Doc2Vec model
        doc2vec_model = Doc2Vec(
            documents=tagged_documents,
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            negative=negative,
            workers=multiprocessing.cpu_count(),
        )

        transformed_column_name = f"_vector_{token_column.replace('_tokens_', '')}"

        X[transformed_column_name] = cls.infer_vectors(
            doc2vec_model=doc2vec_model, token_series=token_series
        )

        return (doc2vec_model, X)
