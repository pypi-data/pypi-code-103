from typing import List, Union

from dagster import Enum, EnumValue, Field
from dask.dataframe import DataFrame as DaskDataFrame
from dask.dataframe import Series as DaskSeries
from dask.dataframe.core import DataFrame
from pandas import DataFrame, Series
from qdk.transform.base import TransformComponent
from stop_words import get_stop_words


class TokenizeComponent(TransformComponent):
    config_schema = {
        "text_columns": Field(
            list,
            default_value=["text"],
            description="Columns to tokenize",
        ),
        "language": Field(
            Enum(
                "Language",
                [
                    EnumValue("en"),
                    EnumValue("nl"),
                ],
            ),
            default_value="nl",
            description="The language of the input text. Used to remove stopwords",
        ),
        "lower": Field(
            bool,
            default_value=True,
            description="Whether to transform the text to lowercase",
        ),
        "remove_numbers": Field(
            bool,
            default_value=True,
            description="Whether to remove numbers from the text",
        ),
        "min_length": Field(
            int,
            default_value=3,
            description="Minimum length of a token",
        ),
        "remove_stop_words": Field(
            bool,
            default_value=True,
            description="Whether to remove stopwords from the text",
        ),
        "join_text": Field(
            bool,
            default_value=False,
            description="Whether join the tokens into one string",
        ),
    }

    @staticmethod
    def _clean_tokens(
        tokens: List[str],
        min_length: int,
        stop_words: List[str],
    ) -> List[str]:
        """Cleans the tokens by removing stop words and short tokens.

        Args:
            tokens (List[str]): The tokens to clean.
            min_length (int): The minimum length of a token to keep.
            stop_words (List[str]): The list of stop words to remove.

        Returns:
            List[str]: The cleaned tokens.
        """
        stop_words_set = set(stop_words)
        return [
            token
            for token in tokens
            if token
            and len(token) >= min_length
            and token.lower() not in stop_words_set
        ]

    @classmethod
    def _tokenize(
        cls,
        series: Union[Series, DaskSeries],
        stop_words: List[str],
        lower: bool,
        remove_numbers: bool,
        min_length: int,
        join_text: bool,
    ) -> Union[Series, DaskSeries]:
        """Function to tokenize a text column.

        Args:
            series (Union[Series, DaskSeries]): The series to tokenize.
            stop_words (List[str]): The list of stop words to remove.
            lower (bool): Whether to transform the text to lowercase.
            remove_numbers (bool): Whether to remove numbers.
            min_length (int): The minimum length of a token.
            join_text (bool): Whether to rejoin the tokens into a string.

        Returns:
            Union[Series, DaskSeries]: The tokenized series.
        """
        # Replace all NaN values with an empty string
        series = series.fillna("")

        # Conditionally lowercase the text
        if lower:
            series = series.str.lower()

        # Remove numbers
        if remove_numbers:
            series = series.str.replace(r"[0-9]", "", regex=True)

        # Tokenize the text
        series = series.str.split(r"\W+")

        # Remove empty tokens
        # Minimum length of tokens
        # Remove stop words
        series = series.map(
            lambda tokens: cls._clean_tokens(tokens, min_length, stop_words)
        )

        # Optionally rejoin the text into a string
        if join_text:
            series = series.str.join(" ")

        return series

    @classmethod
    def transform(
        cls,
        df: Union[DataFrame, DaskDataFrame],
        text_columns: List[str] = ["text"],
        language: str = "nl",
        lower: bool = True,
        remove_numbers: bool = True,
        min_length: int = 3,
        remove_stop_words: bool = True,
        join_text: bool = False,
    ) -> Union[DataFrame, DaskDataFrame]:
        """
        Tokenize certain columns in a dataframe.

        Args:
            df (Union[DataFrame, DaskDataFrame]): The dataframe that contains the text columns.
            text_columns (List[str], optional): The names of the textual columns. Defaults to ["text"].
            language (str, optional): The language of the text, used for stopword removal. Defaults to "nl".
            lower (bool, optional): Whether to lower the text. Defaults to True.
            remove_numbers (bool, optional): Whether to remove numbers. Defaults to True.
            min_length (int, optional): The minimum length of the tokens. Defaults to 3.
            remove_stop_words (bool, optional): Whether to remove stopwords. Defaults to True.
            join_text (bool): Whether to rejoin the tokens into a string. Default to False

        Returns:
            Union[DataFrame, DaskDataFrame]: Return the dataframe with the tokenized columns. The columns are prefixed with "_tokens_".
        """
        # Get stop words for the language specified
        stop_words = get_stop_words(language=language) if remove_stop_words else []

        # Tokenize the text columns specified
        for text_column in text_columns:
            # Get the text column and tokenize it
            df[f"_tokens_{text_column}"] = cls._tokenize(
                series=df[text_column],
                stop_words=stop_words,
                lower=lower,
                remove_numbers=remove_numbers,
                min_length=min_length,
                join_text=join_text,
            )

        return df
