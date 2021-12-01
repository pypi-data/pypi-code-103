import os 
import time 
import numpy as np
import matplotlib.pyplot as plt
from abc import ABCMeta, abstractmethod

from sklearn.utils.extmath import softmax
from sklearn.utils import check_X_y, column_or_1d
from sklearn.utils.validation import check_is_fitted
from sklearn.metrics import make_scorer, mean_squared_error, roc_auc_score
from sklearn.model_selection import GridSearchCV, PredefinedSplit, train_test_split
from sklearn.base import BaseEstimator, RegressorMixin, ClassifierMixin, is_classifier, is_regressor

from .glmtree import GLMTreeRegressor, GLMTreeClassifier

__all__ = ["GLMTreeBoostRegressor"]


class BaseGLMTreeBooster(BaseEstimator, metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, n_estimators, max_depth=3, min_samples_leaf=50, reg_lambda=0, 
                 simplified=False, n_split_grid=20, clip_predict=True, n_jobs=1, verbose=True, val_ratio=0.2, 
                 learning_rate=1.0, early_stop_thres=np.inf, random_state=0):

        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.reg_lambda = reg_lambda
        self.simplified = simplified
        self.n_split_grid = n_split_grid
        self.clip_predict = clip_predict
        self.n_jobs = n_jobs
        
        self.verbose = verbose
        self.val_ratio = val_ratio
        self.learning_rate = learning_rate
        self.early_stop_thres = early_stop_thres
        self.random_state = random_state

    def fit(self, x, y):

        """fit the SimBoost model

        Parameters
        ---------
        x : array-like of shape (n_samples, n_features)
            containing the input dataset
        y : array-like of shape (n_samples,)
            containing target values
        Returns
        -------
        object 
            self : Estimator instance.
        """
        
        start = time.time()
        x, y = self._validate_input(x, y)
        n_samples, n_features = x.shape

        self.estimators_ = []
        self.learning_rates = [1] + [self.learning_rate] * (self.n_estimators - 1)

        if is_regressor(self):
            self.tr_idx, self.val_idx = train_test_split(np.arange(n_samples), test_size=self.val_ratio,
                                          random_state=self.random_state)
        elif is_classifier(self):
            self.tr_idx, self.val_idx = train_test_split(np.arange(n_samples), test_size=self.val_ratio,
                                          stratify=y, random_state=self.random_state)

        self._fit(x, y)
        self.time_cost_ = time.time() - start
        return self

    def decision_function(self, x):

        """output

        Parameters
        ---------
        x : array-like of shape (n_samples, n_features)
            containing the input dataset
        Returns
        -------
        np.array of shape (n_samples,),
        """

        check_is_fitted(self, "estimators_")
        pred = 0
        for indice, est in enumerate(self.estimators_):
            pred += self.learning_rates[indice] * est.predict(x)
        return pred


class GLMTreeBoostRegressor(BaseGLMTreeBooster, RegressorMixin):

    """
    Base class for glmtree boost regression (residual boosting).

    """

    def __init__(self, n_estimators, max_depth=3, min_samples_leaf=50, reg_lambda=0, 
                 simplified=False, n_split_grid=20, clip_predict=True, n_jobs=1, verbose=True, val_ratio=0.2,
                 learning_rate=1.0, early_stop_thres=np.inf, random_state=0):

        super(GLMTreeBoostRegressor, self).__init__(n_estimators=n_estimators,
                                    max_depth=max_depth,
                                    min_samples_leaf=min_samples_leaf,
                                    reg_lambda=reg_lambda,
                                    simplified=simplified,
                                    n_split_grid=n_split_grid,
                                    clip_predict=clip_predict,
                                    n_jobs=n_jobs,
                                    verbose=verbose,
                                    val_ratio=val_ratio,
                                    learning_rate=learning_rate,
                                    early_stop_thres=early_stop_thres,
                                    random_state=random_state)

    def _validate_input(self, x, y):
        
        """method to validate data
        """

        x, y = check_X_y(x, y, accept_sparse=["csr", "csc", "coo"],
                         multi_output=True, y_numeric=True)
        return x, y.ravel()

    def _fit(self, x, y):
   
        """fit the SimBoost model

        Parameters
        ---------
        x : array-like of shape (n_samples, n_features)
            containing the input dataset
        y : array-like of shape (n_samples,)
            containing target values
        """

        # Initialize the intercept
        z = y.copy()
        mse_opt = np.inf
        early_stop_count = 0
        for indice in range(self.n_estimators):
            estimator = GLMTreeRegressor(max_depth=self.max_depth,
                                 min_samples_leaf=self.min_samples_leaf,
                                 reg_lambda=self.reg_lambda,
                                 simplified=self.simplified,
                                 n_split_grid=self.n_split_grid,
                                 clip_predict=self.clip_predict,
                                 n_jobs=self.n_jobs, random_state=self.random_state)
            estimator.fit(x[self.tr_idx], z[self.tr_idx])
            z = z - self.learning_rates[indice] * estimator.predict(x)
            # update
            mse_new = np.mean(z[self.val_idx] ** 2)
            if self.verbose:
                print("Iteration " + str(indice) + " with validation MSE " + str(mse_new))
            if mse_opt > mse_new:
                mse_opt = mse_new
                early_stop_count = 0
            else:
                early_stop_count += 1

            if early_stop_count > self.early_stop_thres:
                break
            self.estimators_.append(estimator)

    def predict(self, x):

        """output prediction for given samples
        
        Parameters
        ---------
        x : array-like of shape (n_samples, n_features)
            containing the input dataset
        Returns
        -------
        np.array of shape (n_samples,)
            containing prediction
        """  

        pred = self.decision_function(x)
        return pred
