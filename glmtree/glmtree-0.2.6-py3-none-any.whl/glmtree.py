import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LassoCV, LogisticRegression, LogisticRegressionCV
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin, MultiOutputMixin
from sklearn.utils.validation import check_is_fitted, _check_sample_weight

from .mobtree import MoBTreeRegressor, MoBTreeClassifier

from warnings import simplefilter
from sklearn.exceptions import ConvergenceWarning
simplefilter("ignore", category=ConvergenceWarning)

from abc import ABCMeta, abstractmethod
from sklearn.linear_model._base import LinearModel
from sklearn.utils.validation import _deprecate_positional_args


class xLinearRegression(MultiOutputMixin, RegressorMixin, LinearModel):
    """
    Marginal Regression Linear Regression.

    Parameters
    ----------
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model. If set
        to False, no intercept will be used in calculations
        (i.e. data is expected to be centered).

    normalize : bool, default=False
        This parameter is ignored when ``fit_intercept`` is set to False.
        If True, the regressors X will be normalized before regression by
        subtracting the mean and dividing by the l2-norm.
        If you wish to standardize, please use
        :class:`~sklearn.preprocessing.StandardScaler` before calling ``fit``
        on an estimator with ``normalize=False``.

    copy_X : bool, default=True
        If True, X will be copied; else, it may be overwritten.

    Attributes
    ----------
    coef_ : array of shape (n_features, ) or (n_targets, n_features)
        Estimated coefficients for the linear regression problem.
        If multiple targets are passed during the fit (y 2D), this
        is a 2D array of shape (n_targets, n_features), while if only
        one target is passed, this is a 1D array of length n_features.

    intercept_ : float or array of shape (n_targets,)
        Independent term in the linear model. Set to 0.0 if
        `fit_intercept = False`.
    """
    @_deprecate_positional_args
    def __init__(self, *, fit_intercept=True, normalize=False, copy_X=True):
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.copy_X = copy_X

    def fit(self, X, y, sample_weight=None):
        """
        Fit linear model.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            Training data

        y : array-like of shape (n_samples,) or (n_samples, n_targets)
            Target values. Will be cast to X's dtype if necessary

        sample_weight : array-like of shape (n_samples,), default=None
            Individual weights for each sample

            .. versionadded:: 0.17
               parameter *sample_weight* support to LinearRegression.

        Returns
        -------
        self : returns an instance of self.
        """

        X, y = self._validate_data(X, y, y_numeric=True, multi_output=True)

        if sample_weight is not None:
            sample_weight = _check_sample_weight(sample_weight, X,
                                                 dtype=X.dtype)
            sample_weight = sample_weight / sample_weight.sum()
        
        X, y, X_offset, y_offset, X_scale = self._preprocess_data(
            X, y, fit_intercept=self.fit_intercept, normalize=self.normalize,
            copy=self.copy_X, sample_weight=sample_weight,
            return_mean=True)

        if sample_weight is not None:
            Xy = np.dot(X.T, y.ravel() * sample_weight)
            mu = np.average(X, axis=0, weights=sample_weight)
            variance = np.diag(np.cov(X.T, aweights=sample_weight))
            self.coef_ = np.divide(Xy, variance, out=np.zeros_like(Xy), where=variance!=0)
            self.coef_ = self.coef_.T
        else:
            Xy = np.dot(X.T, y.reshape(-1, 1)) / X.shape[0]
            variance = np.var(X, axis=0, ddof=1).reshape(-1, 1)
            self.coef_ = np.divide(Xy, variance, out=np.zeros_like(Xy), where=variance!=0)
            self.coef_ = self.coef_.T

        if y.ndim == 1:
            self.coef_ = np.ravel(self.coef_)
        self._set_intercept(X_offset, y_offset, X_scale)
        return self


class GLMTreeRegressor(MoBTreeRegressor, RegressorMixin):

    def __init__(self, max_depth=3, min_samples_leaf=50, min_impurity_decrease=0, feature_names=None, n_jobs=10, simplified=False,
                 split_features=None, n_screen_grid=1, n_feature_search=10, n_split_grid=20, clip_predict=True, reg_lambda=0, random_state=0):

        super(GLMTreeRegressor, self).__init__(max_depth=max_depth,
                                 min_samples_leaf=min_samples_leaf,
                                 min_impurity_decrease=min_impurity_decrease,
                                 feature_names=feature_names,
                                 n_jobs=n_jobs,
                                 split_features=split_features,
                                 n_screen_grid=n_screen_grid,
                                 n_feature_search=n_feature_search,
                                 n_split_grid=n_split_grid,
                                 clip_predict=clip_predict,
                                 random_state=random_state)
        self.simplified = simplified
        self.reg_lambda = reg_lambda
        self.base_estimator = xLinearRegression() if simplified else LinearRegression() 

    def build_root(self):

        self.base_estimator.fit(self.x, self.y)
        root_impurity = self.evaluate_estimator(self.base_estimator, self.x, self.y.ravel())
        return root_impurity

    def build_leaf(self, sample_indice):

        mx = self.x[sample_indice].mean(0)
        sx = self.x[sample_indice].std(0) + self.EPSILON
        nx = (self.x[sample_indice] - mx) / sx

        best_estimator = LassoCV(alphas=self.reg_lambda, cv=5, n_jobs=self.n_jobs, random_state=self.random_state)
        best_estimator.fit(nx, self.y[sample_indice])
        best_estimator.coef_ = best_estimator.coef_ / sx
        best_estimator.intercept_ = best_estimator.intercept_ - np.dot(mx, best_estimator.coef_.T)
        xmin = np.min(np.dot(self.x[sample_indice], best_estimator.coef_) + best_estimator.intercept_)
        xmax = np.max(np.dot(self.x[sample_indice], best_estimator.coef_) + best_estimator.intercept_)
        if self.clip_predict:
            predict_func = lambda x: np.clip(best_estimator.predict(x), xmin, xmax)
        else:
            predict_func = lambda x: best_estimator.predict(x)
        best_impurity = self.get_loss(self.y[sample_indice], best_estimator.predict(self.x[sample_indice]))
        return predict_func, best_estimator, best_impurity


class GLMTreeClassifier(MoBTreeClassifier, ClassifierMixin):

    def __init__(self, max_depth=3, min_samples_leaf=50, min_impurity_decrease=0, feature_names=None, n_jobs=10,
                 split_features=None, n_screen_grid=1, n_feature_search=10, n_split_grid=20, clip_predict=True, reg_lambda=0, random_state=0):

        super(GLMTreeClassifier, self).__init__(max_depth=max_depth,
                                 min_samples_leaf=min_samples_leaf,
                                 min_impurity_decrease=min_impurity_decrease,
                                 feature_names=feature_names,
                                 n_jobs=n_jobs,
                                 split_features=split_features,
                                 n_screen_grid=n_screen_grid,
                                 n_feature_search=n_feature_search,
                                 n_split_grid=n_split_grid,
                                 clip_predict=clip_predict,
                                 random_state=random_state)
        self.n_jobs = n_jobs
        self.reg_lambda = reg_lambda
        self.base_estimator = LogisticRegression(penalty='none', random_state=self.random_state)

    def build_root(self):

        self.base_estimator.fit(self.x, self.y)
        root_impurity = self.evaluate_estimator(self.base_estimator, self.x, self.y.ravel())
        return root_impurity

    def build_leaf(self, sample_indice):

        if (self.y[sample_indice].std() == 0) | (self.y[sample_indice].sum() < 5) | ((1 - self.y[sample_indice]).sum() < 5):
            best_estimator = None
            predict_func = lambda x: np.ones(x.shape[0]) * self.y[sample_indice].mean()
            best_impurity = self.get_loss(self.y[sample_indice], predict_func(self.x[sample_indice]))
        else:
            best_estimator = LogisticRegressionCV(Cs=self.reg_lambda, penalty="l1", solver="liblinear", scoring="roc_auc",
                                      cv=5, n_jobs=self.n_jobs, random_state=self.random_state)
            mx = self.x[sample_indice].mean(0)
            sx = self.x[sample_indice].std(0) + self.EPSILON
            nx = (self.x[sample_indice] - mx) / sx
            best_estimator.fit(nx, self.y[sample_indice])
            best_estimator.coef_ = best_estimator.coef_ / sx
            best_estimator.intercept_ = best_estimator.intercept_ - np.dot(mx, best_estimator.coef_.T)
            xmin = np.min(np.dot(self.x[sample_indice], best_estimator.coef_.ravel()))
            xmax = np.max(np.dot(self.x[sample_indice], best_estimator.coef_.ravel()))
            if self.clip_predict:
                predict_func = lambda x: 1 / (1 + np.exp(- np.clip(np.dot(x, best_estimator.coef_.ravel()),
                                   xmin, xmax) - best_estimator.intercept_))
            else:
                predict_func = lambda x: 1 / (1 + np.exp(- np.dot(x, best_estimator.coef_.ravel()) - best_estimator.intercept_))
            best_impurity = self.get_loss(self.y[sample_indice], best_estimator.predict_proba(self.x[sample_indice])[:, 1])
        return predict_func, best_estimator, best_impurity
