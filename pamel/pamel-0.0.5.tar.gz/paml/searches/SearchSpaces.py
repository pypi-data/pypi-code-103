from enum import Enum
import numpy as np

class SearchSpaces(Enum):
    DECISION_TREE_CLASSIFIER = [{'estimator': ['decision_tree'],
                                'criterion': ['gini', 'entropy'],
                                'splitter': ['best', 'random'],
                                'max_depth': [3, 5, 8,10, 15],
                                'max_features': ['auto', 'sqrt', 'log2'],
                                'random_state': [42], }]

    XGB_CLASSIFIER =    [{'estimator': ['xgb'],
                        'n_estimators':[1500],
                        'use_label_encoder': [False],
                        'eta': list(np.linspace(0, 0.6, 3, dtype=float)),
                        'gamma':list(np.linspace(0, 0.3, 3,  dtype=float)),
                        'use_label_encoder': [False],
                        'objective': ['binary:logistic'],
                        'n_estimators': [300, 500],
                        'eval_metric': ["logloss"],
                        'seed': [42],
                        'learning_rate': np.linspace(1e-5, 0.01, 3),
                        'gamma': np.linspace(0, 1, 2),
                        'max_depth':np.arange(3, 10, 2),
                        'min_child_weight': [1],
                        'subsample': np.linspace(0.5, 1, 3),
                        'colsample_bytree': np.linspace(0.5, 1, 3),
                        'alpha': np.linspace(1e-8, 10, 5),
                        'lambda': np.linspace(1e-8, 10, 5)}]

    
    CATBOOST_CLASSIFIER =  [{'estimator': ['catboost'],
                            'n_estimators': [500,1500],
                            'early_stopping_rounds': [50],
                            'eval_metric': ["AUC", "Logloss"],
                            'random_state': [42],
                            'learning_rate': np.linspace(1e-5, 0.01, 3),
                            'max_depth': [6, 8, 12],
                            'min_data_in_leaf': [20, 30, 50],
                            'colsample_bylevel': np.linspace(0.5, 1),
                            'boosting_type': ["Plain", "Ordered"],
                            'l2_leaf_reg': [1, 5, 7],
                            'loss_function': ['Logloss'],
                            'bootstrap_type':['Bayesian', 'Bernoulli', 'MVS']}]

    ADABOOST_CLASSIFIER =   [{'estimator': ['adaboost'],
                                'n_estimators': [1000],
                                'algorithm': ["SAMME", "SAMME.R"],
                                'max_leaf_nodes': [16, 32]}]

    LGBM_CLASSIFIER = [{'estimator': ['lgbm'],
                        'objective': ['binary'],
                        'num_iterations': [1500],
                        'metric': ["auc", "logloss"],
                        'seed': [42],
                        'boosting': ['gbdt'],
                        'num_leaves':[16, 32, 64],
                        'learning_rate': [1e-5, 1e-3, 1e-2],
                        'max_depth': [2, 5, 7],
                        'min_data_in_leaf': [20, 50, 100],
                        'min_sum_hessian_in_leaf': [1e-5, 1e-3, 1e-2],
                        'lambda_l1': np.linspace(1e-3, 1, 3),
                        'lambda_l2': np.linspace(1e-3, 1, 3),
                        'bagging_freq': [5, 7],
                        'bagging_fraction': [0.2, 0.5, 1.0],
                        'feature_fraction': [0.6, 0.8, 1.0],
                        'feature_fraction_bynode': [0.6, 0.8, 1.0],
                        'min_data_per_group': [50, 100, 300],
                        'cat_l2': [20, 30],
                        'cat_smooth': [20, 30]}]

    LOGISTIC_REGRESSION = [{'estimator': ['logistic_regressor'],
                            'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
                            'C': [1, 0.8, 0.7, 0.5, 0.3]}]


    DECISION_TREE_REGRESSOR = [{'estimator': ['decision_tree'],
                                'criterion': ['squared_error', 'friedman_mse', 'poisson'],
                                'splitter': ['best', 'random'],
                                'max_depth': [3, 5, 8, 10, 15],
                                'max_features': ['auto', 'sqrt', 'log2'],
                                'random_state': [42]}]

    XGB_REGRESSOR =    [{'estimator': ['xgb'],
                        'eta': list(np.linspace(0, 0.6, 3, dtype=float)),
                        'gamma':list(np.linspace(0, 0.3, 3,  dtype=float)),
                        'n_estimators': [300, 500],
                        'eval_metric': ["rmse"],
                        'seed': [42],
                        'learning_rate': np.linspace(1e-3, 0.01, 3),
                        'gamma': np.linspace(0, 0.5, 3),
                        'max_depth':np.arange(6, 15, 3),
                        'subsample': np.linspace(0.5, 1, 3),
                        'colsample_bytree': np.linspace(0, 1, 3),
                        'alpha': np.linspace(1e-8, 1, 3),
                        'lambda': np.linspace(1e-8, 1, 3)}]

   
    CATBOOST_REGRESSOR =  [{'estimator': ['catboost'],
                        'n_estimators': [1500],
                        'early_stopping_rounds': [50],
                        'eval_metric': ['RMSE'],
                        'random_state': [42],
                        'learning_rate': np.linspace(1e-5, 0.01, 3),
                        'max_depth': [7, 10, 12],
                        'min_data_in_leaf': [10, 30, 50],
                        'colsample_bylevel': [0.5, 1],
                        'boosting_type': ['Plain', 'Ordered'],
                        'l2_leaf_reg': [1, 5, 10],
                        'loss_function': ['RMSE'],
                        'bootstrap_type': ['Bayesian', 'Bernoulli', 'MVS']}]

    ADABOOST_REGRESSOR =   [{'estimator': ['adaboost'],
                            'n_estimators': [1000],
                            'loss': ["linear", "square", "exponenctial"],
                            'learning_rate': np.linspace(0.3, 1, 3), }]

    LGBM_REGRESSOR =    [{'estimator': ['lgbm'],
                        'objective': ['regression'],
                        'n_estimators': [1500],
                        'metric': ["rmse", "R2"],
                        'random_state': [42],
                        'boosting': ['gbdt'],
                        'num_leaves':[16, 32, 64],
                        'learning_rate': [1e-5, 1e-3, 1e-1],
                        'max_depth': [2, 5, 7],
                        'min_data_in_leaf': [10, 20, 50],
                        'min_sum_hessian_in_leaf': [1e-3, 1e-2, 1e-1],
                        'reg_alpha': np.linspace(1e-3, 1, 3),
                        'reg_lambda': np.linspace(1e-3, 1, 3),
                        'feature_fraction': [0.7, 0.8, 1.0],
                        'feature_fraction_bynode': [0.6, 0.8, 1.0],
                        'min_data_per_group': [100, 200],
                        'bagging_freq': [5, 7],
                        'bagging_fraction': [0.5, 0.7, 1.0],
                        'cat_l2': [10, 20, 50],
                        'categorical_feature': ['auto'],
                        'cat_smooth': [10, 20, 50]}]

    SVR  =           [{'estimator': ['svr'],
                    'kernel': ["linear", "poly", "sigmoid"],
                    'gamma':["scale", "auto"],
                    'C':[0.2, 0.5, 1],
                    'epsilon': [1e-2, 1-3, 1]}]

def get_enum(model, task):
    if task == 'classification':
        if model == 'decision_tree':
            return SearchSpaces.DECISION_TREE_CLASSIFIER.value
        elif model == 'xgb':
            return SearchSpaces.XGB_CLASSIFIER.value
        elif model == 'catboost':
            return SearchSpaces.CATBOOST_CLASSIFIER.value
        elif model == 'adaboost':
            return SearchSpaces.ADABOOST_CLASSIFIER.value
        elif model == 'lgbm':
            return SearchSpaces.LGBM_CLASSIFIER.value
        elif model == 'logistic_regression':
            return SearchSpaces.LOGISTIC_REGRESSION.value
        else:
            raise BaseException("Model not added to the tool yet")
    elif task == 'regression':
        if model == 'decision_tree':
            return SearchSpaces.DECISION_TREE_REGRESSOR.value
        elif model == 'xgb':
            return SearchSpaces.XGB_REGRESSOR.value
        elif model == 'catboost':
            return SearchSpaces.CATBOOST_REGRESSOR.value
        elif model == 'adaboost':
            return SearchSpaces.ADABOOST_REGRESSOR.value
        elif model == 'lgbm':
            return SearchSpaces.LGBM_REGRESSOR.value
        elif model == 'svr':
            return SearchSpaces.SVR.value
        else:
            raise BaseException("Model not added to the tool yet")
    else:
        raise BaseException("Task not implemented yet")
    


