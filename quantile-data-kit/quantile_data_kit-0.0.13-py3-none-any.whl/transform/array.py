from typing import Union
from pandas.core.series import Series
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import dask.dataframe as dd


class ArrayTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(
        self,
        X: Union[pd.DataFrame, dd.DataFrame],
        y: Union[pd.Series, dd.Series] = None,
    ):

        if isinstance(X, pd.DataFrame):
            return X.to_numpy()
        elif isinstance(X, dd.DataFrame):
            return X.to_dask_array()
