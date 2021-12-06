"""Custom Transformers"""
from typing import List

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CustomImputer(BaseEstimator, TransformerMixin):
    """
    Class used for imputing missing values in a pd.DataFrame.
    """

    def __init__(self, missing_values: List[int], value: int):
        """Init function."""
        self.missing_values = missing_values
        self.value = value

    def fit(self, X, y=None):
        """Fit function."""
        return self

    def transform(self, X, y=None):
        """Transform function."""
        X = X.copy()

        X.replace(
            {element: self.value for element in self.missing_values}, inplace=True
        )

        return pd.DataFrame(X)
