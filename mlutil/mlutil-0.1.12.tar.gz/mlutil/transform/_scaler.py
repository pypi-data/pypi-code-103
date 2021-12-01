from typing import Optional, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class SigmaClipper(TransformerMixin, BaseEstimator):
    """Clip values exceeding specified sigma levels from median

    :param sigma: both low_sigma and high_sigma
    :param low_sigma: low sigma level (aabsolute value)
        Overrides sigma
    :param max_sigma: high sigma level (aabsolute value)
        Overrides sigma
    :param mean_fun: 'median' | 'mean'
    """

    def __init__(
        self,
        sigma: Optional[float] = 3.0,
        low_sigma: Optional[float] = None,
        high_sigma: Optional[float] = None,
        mean_fun: str = "median",
    ):
        self.sigma = sigma
        self.low_sigma = low_sigma
        self.high_sigma = high_sigma
        self.mean_fun = mean_fun

    def fit(self, X: Union[np.ndarray, pd.DataFrame], y=None):
        self.low_sigma_ = self.sigma if self.low_sigma is None else self.low_sigma
        self.high_sigma_ = self.sigma if self.high_sigma is None else self.high_sigma
        assert (self.low_sigma_ is not None) and (self.low_sigma_ >= 0)
        assert (self.high_sigma_ is not None) and (self.high_sigma_ >= 0)

        if self.mean_fun == "median":
            meanf = np.nanmedian
        elif self.mean_fun == "mean":
            meanf = np.nanmean  # type: ignore
        else:
            raise ValueError(self.mean_fun)
        X_ = np.asarray(X)
        self.mean_ = meanf(X_, axis=0)
        self.std_ = np.sqrt(meanf((X_ - self.mean_) ** 2, axis=0))
        self.high_ = self.mean_ + self.low_sigma_ * self.std_
        self.low_ = self.mean_ - self.high_sigma_ * self.std_
        return self

    def transform(self, X: Union[np.ndarray, pd.DataFrame]) -> Union[np.ndarray, pd.DataFrame]:
        if isinstance(X, pd.DataFrame):
            X = X.clip(self.low_, self.high_, axis=1)
        else:
            X = np.clip(X, self.low_[np.newaxis, :], self.high_[np.newaxis, :])
        return X


class QuantileClipper(TransformerMixin, BaseEstimator):
    """Clip values exceeding specified quantile levels times a factor

    :param factor: multiplier
    :param low_quantile: low quantile level
    :param high_quantile: high quantile level
    :param mean_fun: 'median' | 'mean'
    """

    def __init__(
        self,
        factor: float = 3.0,
        low_quantile: Optional[float] = 0.9,
        high_quantile: Optional[float] = 0.1,
        mean_fun: str = "median",
    ):
        self.factor = factor
        self.low_quantile = low_quantile
        self.high_quantile = high_quantile
        self.mean_fun = mean_fun

    def fit(self, X: Union[np.ndarray, pd.DataFrame], y=None):
        assert self.factor >= 0
        X_ = np.asarray(X)
        self.mean_ = np.nanmedian(X_, axis=0)
        self.high_q_ = np.nanquantile(X_, self.high_quantile, axis=0)
        self.low_q_ = np.nanquantile(X_, self.low_quantile, axis=0)
        self.high_ = (self.high_q_ - self.mean_) * self.factor + self.mean_
        self.low_ = (self.low_q_ - self.mean_) * self.factor + self.mean_
        return self

    def transform(self, X: Union[np.ndarray, pd.DataFrame]) -> Union[np.ndarray, pd.DataFrame]:
        if isinstance(X, pd.DataFrame):
            X = X.clip(self.low_, self.high_, axis=1)
        else:
            X = np.clip(X, self.low_[np.newaxis, :], self.high_[np.newaxis, :])
        return X
