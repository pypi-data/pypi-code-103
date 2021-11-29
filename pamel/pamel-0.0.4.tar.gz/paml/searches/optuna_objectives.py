import pandas as pd

from sklearn.metrics import roc_auc_score
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVR

from xgboost import XGBClassifier, XGBRegressor
from catboost import CatBoostClassifier, CatBoostRegressor, Pool
from lightgbm import LGBMClassifier, LGBMRegressor

from paml.metrics import Metrics


class OptunaObjectives:
    def __objective_xgb_clf__(trial, X, y):
        params = {
            
            'use_label_encoder': False,
            'objective': 'binary:logistic',
            'n_estimators': 1000,
            'eval_metric': ["auc", "logloss"],
            'seed': 42,
            'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-2),
            'gamma': trial.suggest_uniform('gamma', 0, 1),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'min_child_weight': trial.suggest_int('min_child_weight', 0, 10),
            'subsample': trial.suggest_uniform('subsample', 0.5, 1),
            'colsample_bytree': trial.suggest_uniform('colsample_bytree', 0, 1),
            'alpha': trial.suggest_loguniform('alpha', 1e-8, 10.0),
            'lambda': trial.suggest_loguniform('lambda', 1e-8, 10.0)
        }
        xgbClassifier = XGBClassifier(**params)

        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass

        X = pd.get_dummies(X, drop_first = True)
        xgbClassifier.fit(X, y)
        y_pred = xgbClassifier.predict(X)
        return roc_auc_score(y, y_pred)

    def __objective_xgb_regressor__(trial, X, y):
        params = {
            'n_estimators': 1000,
            'eval_metric': trial.suggest_categorical("eval_metric", ["rmse"]),
            'seed': 42,
            'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-2),
            'gamma': trial.suggest_uniform('gamma', 0, 1),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'min_child_weight': trial.suggest_int('min_child_weight', 0, 10),
            'subsample': trial.suggest_uniform('subsample', 0.5, 1),
            'colsample_bytree': trial.suggest_uniform('colsample_bytree', 0, 1),
            'alpha': trial.suggest_loguniform('alpha', 1e-8, 10.0),
            'lambda': trial.suggest_loguniform('lambda', 1e-8, 10.0)
        }
        xgbRegressor = XGBRegressor(**params)

        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass

        X = pd.get_dummies(X, drop_first = True)
        xgbRegressor.fit(X, y)
        y_pred = xgbRegressor.predict(X)
        return Metrics.__theil_stat__(y, y_pred)

    def __objective_catboost_classifier__(trial, X, y):
        params = {
            'n_estimators': trial.suggest_int('n_estimators',  200, 500),
            'early_stopping_rounds': 50,
            'eval_metric': trial.suggest_categorical('eval_metric', ['AUC', 'Logloss']),
            'random_state': 42,
            'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-2),
            'max_depth': trial.suggest_int('max_depth',  3, 8),
            'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 10, 100),
            'colsample_bylevel': trial.suggest_uniform('colsample_bylevel', 0.5, 1),
            'boosting_type': trial.suggest_categorical('boosting_type', ['Plain', 'Ordered']),
            'l2_leaf_reg': trial.suggest_int('l2_leaf_reg', 1, 10),
            'loss_function': trial.suggest_categorical('loss_function', ['Logloss']),
            'bootstrap_type': trial.suggest_categorical('bootstrap_type', ['Bayesian', 'Bernoulli', 'MVS'])
        }

        catboostClassifier = CatBoostClassifier(**params)

        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass

        cat_features_index = [X.columns.get_loc(
            x) for x in X.columns if X[x].dtypes == 'object']

        pool = Pool(X, label=y, cat_features=cat_features_index)
        catboostClassifier.fit(pool)

        y_pred = catboostClassifier.predict(pool)
        return roc_auc_score(y, y_pred)

    def __objective_catboost_regressor__(trial, X, y):
        params = {
            'n_estimators': 1000,
            'early_stopping_rounds': 50,
            'eval_metric': trial.suggest_categorical('eval_metric', ['RMSE']),
            'random_state': 42,
            'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-2),
            'max_depth': trial.suggest_int('max_depth',  3, 8),
            'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 10, 100),
            'colsample_bylevel': trial.suggest_uniform('colsample_bylevel', 0.5, 1),
            'boosting_type': trial.suggest_categorical('boosting_type', ['Plain', 'Ordered']),
            'l2_leaf_reg': trial.suggest_int('l2_leaf_reg', 1, 10),
            'loss_function': trial.suggest_categorical('loss_function', ['RMSE']),
            'bootstrap_type': trial.suggest_categorical('bootstrap_type', ['Bayesian', 'Bernoulli', 'MVS'])
        }
        catboostRegressor = CatBoostRegressor(**params)
        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass

        cat_features_index = [X.columns.get_loc(
            x) for x in X.columns if X[x].dtypes == 'object']

        pool = Pool(X, label=y, cat_features=cat_features_index)

        catboostRegressor.fit(pool)

        y_pred = catboostRegressor.predict(pool)
        return Metrics.__theil_stat__(y, y_pred)

    def __objective_lgbm_classifier__(trial, X, y):
        params = {
            'objective': 'binary',
            'n_estimators': 1500,
            'eval_metric': trial.suggest_categorical('metric', ['AUC']),
            'seed': 42,
            'boosting': trial.suggest_categorical('boosting', ['gbdt']),
            'num_leaves': trial.suggest_int('num_leaves', 2, 256),
            'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-2),
            'max_depth': trial.suggest_int('max_depth', 0, 7),
            'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 10, 100),
            'min_sum_hessian_in_leaf': trial.suggest_loguniform('min_sum_hessian_in_leaf', 1e-5, 1e-1),
            'reg_alpha': trial.suggest_loguniform('reg_alpha', 1e-8, 10.0),
            'reg_lambda': trial.suggest_loguniform('reg_lambda', 1e-8, 10.0),
            'bagging_freq': 5,
            'bagging_fraction': trial.suggest_uniform('bagging_fraction', 0.1, 1.0),
            'feature_fraction': trial.suggest_uniform('feature_fraction', 0.4, 1.0),
            'feature_fraction_bynode': trial.suggest_uniform('feature_fraction', 0.4, 1.0),
            'min_data_per_group': trial.suggest_int('min_data_per_group', 50, 300),
            'cat_l2': trial.suggest_int('cat_l2', 1, 100),
            'cat_smooth': trial.suggest_int('cat_smooth', 1, 100)
        }

        LGBMClf = LGBMClassifier(**params)

        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass

        X = pd.get_dummies(X, drop_first=True)
        LGBMClf.fit(X, y, eval_set=[(X, y)])
        y_pred = LGBMClf.predict(X)
        return roc_auc_score(y, y_pred)

    def __objective_lgbm_regressor__(trial, X, y):
        params = {
            'objective': 'binary',
            'n_estimators': 1500,
            'eval_metric': trial.suggest_categorical('metric', ['rmse']),
            'seed': 42,
            'boosting': trial.suggest_categorical('boosting', ['gbdt']),
            'num_leaves': trial.suggest_int('num_leaves', 2, 256),
            'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-1),
            'max_depth': trial.suggest_int('max_depth', 0, 7),
            'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 10, 100),
            'min_sum_hessian_in_leaf': trial.suggest_loguniform('min_sum_hessian_in_leaf', 1e-5, 1e-2),
            'reg_alpha': trial.suggest_loguniform('reg_alpha', 1e-8, 10.0),
            'reg_lambda': trial.suggest_loguniform('reg_lambda', 1e-8, 10.0),
            'bagging_freq': 5,
            'bagging_fraction': trial.suggest_uniform('bagging_fraction', 0.1, 1.0),
            'feature_fraction': trial.suggest_uniform('feature_fraction', 0.4, 1.0),
            'feature_fraction_bynode': trial.suggest_uniform('feature_fraction', 0.4, 1.0),
            'min_data_per_group': trial.suggest_int('min_data_per_group', 50, 300),
            'cat_l2': trial.suggest_int('cat_l2', 1, 100),
            'cat_smooth': trial.suggest_int('cat_smooth', 1, 100)
        }

        LGBMRgs = LGBMRegressor(**params)

        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass

        X = pd.get_dummies(X, drop_first=True)
        LGBMRgs.fit(X, y, eval_set=[(X, y)])
        y_pred = LGBMRgs.predict(X)
        return Metrics.__theil_stat__(y, y_pred)

    def __objective_decision_tree_classifier__(trial, X, y):
        params = {'criterion': trial.suggest_categorical('criterion', ['gini', 'entropy']),
                  'splitter': trial.suggest_categorical('splitter', ['best', 'random']),
                  'max_depth': trial.suggest_int('max_depth', 2, 12),
                  'max_features': trial.suggest_categorical('max_features', ['auto', 'sqrt', 'log2']),
                  'random_state': 42}
        DTClassifier = DecisionTreeClassifier(**params)

        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass

        X = pd.get_dummies(X, drop_first=True)
        DTClassifier.fit(X, y)

        y_pred = DTClassifier.predict(X)
        return roc_auc_score(y, y_pred)

    def __objective_decision_tree_regressor__(trial, X, y):
        params = {'criterion': trial.suggest_categorical('criterion', ['mse', 'friedman_mse', 'poisson']),
                  'splitter': trial.suggest_categorical('splitter', ['best', 'random']),
                  'max_depth': trial.suggest_int('max_depth', 2,  12),
                  'max_features': trial.suggest_categorical('max_features', ['auto', 'sqrt', 'log2']),
                  'random_state': 42}
        DTRegressor = DecisionTreeRegressor(**params)


        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass


        X = pd.get_dummies(X, drop_first=True)
        DTRegressor.fit(X, y)

        y_pred = DTRegressor.predict(X)
        return Metrics.__theil_stat__(y, y_pred)

    def __objective_adaboost_classifier__(trial, X, y):
        params = {'n_estimators': trial.suggest_int('n_estimators', 500, 1500),
                  'algorithm': trial.suggest_categorical('algorithm', ["SAMME", "SAMME.R"]),
                  'learning_rate': trial.suggest_uniform('learning_rate', 1e-2,  1), }

        adaboost_clf = AdaBoostClassifier(**params)

        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass

        X = pd.get_dummies(X, drop_first=True)
        adaboost_clf.fit(X, y)
        y_pred = adaboost_clf.predict(X)
        return roc_auc_score(y, y_pred)

    def __objective_adaboost_regressor__(trial, X, y):
        params = {'n_estimators': trial.suggest_int('n_estimators', 500, 1500),
                  'loss': trial.suggest_categorical('loss', ["linear", "square", "exponential"]),
                  'learning_rate': trial.suggest_uniform('learning_rate', 1e-2,  1), }

        adaboostRegressor = AdaBoostRegressor(**params)

        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass

        X = pd.get_dummies(X, drop_first=True)
        adaboostRegressor.fit(X, y)
        y_pred = adaboostRegressor.predict(X)
        return Metrics.__theil_stat__(y, y_pred)

    def __objective__logistic_regression__(trial, X, y):
        params = {'solver': trial.suggest_categorical('solver', ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']),
                  'C': trial.suggest_uniform('C', 0.3, 1)}
        logistic = LogisticRegression(**params)

        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass


        X = pd.get_dummies(X, drop_first=True)
        logistic.fit(X, y)
        y_pred = logistic.predict(X)
        return roc_auc_score(y, y_pred)

    def __objective_svr_regressor__(trial, X, y):
        params = {'kernel': trial.suggest_categorical('kernel', ["linear", "poly", "sigmoid"]),
                  'gamma': trial.suggest_categorical('gamma', ["scale", "auto"]),
                  'C': trial.suggest_uniform('C', 0.2, 1),
                  'epsilon': trial.suggest_uniform('epsilon', 1e-2, 1)}

        svr = SVR(**params)

        try:
            numeric_features = [col for col in X.columns if X[col].dtypes == 'int64' or X[col].dtypes == 'float64' 
                                or X[col].dtypes == 'int' or X[col].dtypes == 'float']
            if numeric_features:
                for feat in numeric_features:
                    X.loc[X.columns == feat] = X[feat].astype('float64')
        except:
            pass

        X = pd.get_dummies(X, drop_first=True)
        svr.fit(X, y)
        y_pred = svr.predict(X)
        return Metrics.__theil_stat__(y, y_pred)
