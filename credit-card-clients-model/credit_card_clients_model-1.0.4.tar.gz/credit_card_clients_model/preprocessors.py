from typing import List
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


# categorical missing value imputer
class CategoricalReplacer(BaseEstimator, TransformerMixin):
    def __init__(self, categories_to_replace: List[int], value: int):
        self.categories_to_replace = categories_to_replace
        self.value = value

    def fit(self, X, y=None):
        # we need the fit statement to accomodate the sklearn pipeline
        return self

    def transform(self, X):
        X_ = X.copy()

        X_.replace(
            {item: self.value for item in self.categories_to_replace},
            inplace=True,
        )

        return pd.DataFrame(X_)
