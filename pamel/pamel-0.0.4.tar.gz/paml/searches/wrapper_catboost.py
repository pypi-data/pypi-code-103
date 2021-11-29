from catboost import CatBoostClassifier, CatBoostRegressor, Pool
from pandas.api.types import is_numeric_dtype
import pandas as pd
import numpy as np

class CatBoostClassifierScikit:
    def __init__(self, params={}) -> None:
        self.classifier = CatBoostClassifier(**params)

    def fit(self, X, y):
        if type(X) == np.ndarray:
            X = pd.DataFrame(X)

        cat_index = [X.columns.get_loc(
            x) for x in X.columns if X[x].dtypes == 'object']
        numeric_features_index = [X.columns.get_loc(x) for x in X.columns if is_numeric_dtype(X[x])]
        for feat in X.columns:
            if feat in X.columns[numeric_features_index]:
                X[feat] = X[feat].astype('float')
        pool  = Pool(data=X[X.columns], label=y, cat_features=cat_index)
        self.classifier.fit(pool)

        return self

    def predict(self, X, y=None):
        if type(X) == np.ndarray:
            X = pd.DataFrame(X)

        cat_index = [X.columns.get_loc(
            x) for x in X.columns if X[x].dtypes == 'object']
        numeric_features_index = [X.columns.get_loc(x) for x in X.columns if is_numeric_dtype(X[x])]
        for feat in X.columns:
            if feat in X.columns[numeric_features_index]:
                X[feat] = X[feat].astype('float')
        pool  = Pool(data=X[X.columns], label=y, cat_features=cat_index)
        return self.classifier.predict(pool)


    def predict_proba(self, X, y=None):
        if type(X) == np.ndarray:
            X = pd.DataFrame(X)

        cat_index = [X.columns.get_loc(
            x) for x in X.columns if X[x].dtypes == 'object']
        numeric_features_index = [X.columns.get_loc(x) for x in X.columns if is_numeric_dtype(X[x])]
        for feat in X.columns:
            if feat in X.columns[numeric_features_index]:
                X[feat] = X[feat].astype('float')
        pool  = Pool(data=X[X.columns], label=y, cat_features=cat_index)
        return self.classifier.predict_proba(pool)

    def set_params(self, **params):
        self.classifier.set_params(**params)


       
class CatBoostRegressorScikit:
    def __init__(self, params={}):
        self.regressor = CatBoostRegressor(**params)
        # super().__init__(loss_function=None)

    def fit(self, X, y):
        if type(X) == np.ndarray:
            X = pd.DataFrame(X)

        cat_index = [X.columns.get_loc(
            x) for x in X.columns if X[x].dtypes == 'object']
        numeric_features_index = [X.columns.get_loc(x) for x in X.columns if is_numeric_dtype(X[x])]
        for feat in X.columns:
            if feat in X.columns[numeric_features_index]:
                X[feat] = X[feat].astype('float')
        pool  = Pool(data=X[X.columns], label=y, cat_features=cat_index)
        self.regressor.fit(pool)

        return self

    def predict(self, X, y=None):
        if type(X) == np.ndarray:
            X = pd.DataFrame(X)

        cat_index = [X.columns.get_loc(
            x) for x in X.columns if X[x].dtypes == 'object']
        numeric_features_index = [X.columns.get_loc(x) for x in X.columns if is_numeric_dtype(X[x])]
        for feat in X.columns:
            if feat in X.columns[numeric_features_index]:
                X[feat] = X[feat].astype('float')
        pool  = Pool(data=X[X.columns], label=y, cat_features=cat_index)
        return self.regressor.predict(pool)


    def set_params(self, **params):
        self.regressor.set_params(**params)

    @property
    def boosting_type(self, boosting_type):
        self.regressor.boosting_type = boosting_type