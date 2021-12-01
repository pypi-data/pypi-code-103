from typing import List, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from statsmodels.gam.api import BSplines, CyclicCubicSplines, GLMGam


class GAM(RegressorMixin, BaseEstimator):
    """Generalized Additive Models

    :param splines: type of spline functions
        'cyclic_cubic' | 'b'
    :param df: number of spline basis functions (= knots)
        if splines='cyclic_cubic', must be set to 3 (default value)
    :param degree: degree of splines
    :param family: distribution gamily (default: gaussian)
        See statsmodels.api.families
    :param alpha: penalization weight
    :param clip_X: if true, clip X values by its min and max during training
        use for 'b' splines, which do not have extrapolation
    """

    def __init__(
        self,
        splines: str = "cyclic_cubic",
        df: Union[int, List[int]] = 5,
        degree: Union[int, List[int]] = 3,
        family=None,
        alpha: Union[float, List[float]] = 0.01,
        clip_X: bool = False,
    ):
        self.df = df
        self.degree = degree
        self.family = family
        self.alpha = alpha
        self.splines = splines
        self.clip_X = clip_X

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]):
        assert not (self.splines == "cyclic_cubic") or (self.degree == 3)
        df = self.df if isinstance(self.df, list) else [self.df] * X.shape[1]
        degree = self.degree if isinstance(self.degree, list) else [self.degree] * X.shape[1]
        alpha = self.alpha if isinstance(self.alpha, list) else [self.alpha] * X.shape[1]
        if self.splines == "cyclic_cubic":
            self.splines_ = CyclicCubicSplines(X, df=df)
        elif self.splines == "b":
            self.splines_ = BSplines(X, df=df, degree=degree)
        else:
            raise ValueError(self.splines)
        self.x_min_ = np.min(X, axis=0)
        self.x_max_ = np.max(X, axis=0)
        self.estimator_ = GLMGam(y, X, smoother=self.splines_, family=self.family, alpha=alpha)
        self.res_ = self.estimator_.fit()
        return self

    def predict(self, X: Union[pd.DataFrame, np.ndarray]):
        if self.clip_X:
            X = np.clip(X, self.x_min_, self.x_max_)
        return self.res_.predict(X, exog_smooth=X)

    def summary(self):
        return self.res_.summary()

    @property
    def feature_names(self) -> List[str]:
        return self.estimator_.exog_names
