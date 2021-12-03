from sklearn.svm import SVR, SVC
from hyperopt import hp
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.gaussian_process import GaussianProcessRegressor, GaussianProcessClassifier
from catboost import CatBoostRegressor, CatBoostClassifier
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier, RandomForestRegressor, \
    RandomForestClassifier
from ..utils.base_func import linspace

reg_dict = [
    {SVR: {}},
    {DecisionTreeRegressor: {}},
    {XGBRegressor: {}},
    {LGBMRegressor: {}},
    {LinearRegression: {}},
    {GaussianProcessRegressor: {}},
    {CatBoostRegressor: {"verbose": False, "iterations": 30}},
    {GradientBoostingRegressor: {}},
    # {RandomForestRegressor: {"random_state": 0}}
]

reg_list = [SVR, DecisionTreeRegressor, XGBRegressor, LGBMRegressor, LinearRegression, GaussianProcessRegressor,
            CatBoostRegressor, GradientBoostingRegressor, RandomForestRegressor]

cls_list = [
    SVC, DecisionTreeClassifier, XGBClassifier, LGBMClassifier, LogisticRegression, GaussianProcessClassifier, CatBoostClassifier
]

gridsearch_parameters_reg = {
    XGBRegressor: {
        "learning_rate": linspace(0.05, 1, 0.05),
        "n_estimators": linspace(50, 350, 10, dtype=int),
        # "gamma": linspace(0, 1, 0.1),
        # "lambda": linspace(0, 0.5, 0.1),
        # "alpha": linspace(0.5, 1, 0.1),
        "max_depth": linspace(3, 8, 1, dtype=int),
        "n_jobs": [1]
    },
    GradientBoostingRegressor: {
        "learning_rate": linspace(0.05, 1, 0.05),
        "n_estimators": linspace(50, 350, 10, dtype=int),
        "max_depth": linspace(3, 8, 1, dtype=int)
    },
    LGBMRegressor: {
        "learning_rate": linspace(0.05, 1, 0.05),
        "n_estimators": linspace(50, 350, 10, dtype=int),
        "max_depth": linspace(3, 8, 1, dtype=int),
    },
    CatBoostRegressor: {
        # "learning_rate": linspace(0.01, 0.5, 0.02),
        "max_depth": linspace(4, 10, 1, dtype=int),
        "n_estimators": linspace(50, 600, 50, dtype=int),
        "verbose": [False],
        "thread_count": [1]
    }
}

gridsearch_parameters_cls = {}

gridsearch_parameters = {
    "reg": gridsearch_parameters_reg,
    "cls": gridsearch_parameters_cls
}

class AutoConfig(object):

    feature_selection = {
        "algorithms": hp.choice("algorithms", reg_dict),
    }

    split_data = {
        "algorithms": hp.choice("algorithms", reg_dict),
        "random_state": hp.randint("random_state", 0, 9999),
        "test_size": hp.uniform("test_size", 0.05, 0.40)
    }

    regression = hp.choice("algorithms", [
        {
            "algo": SVR,
            "kwargs": {
                "C": hp.uniform("svr_C", 0, 20),
                "gamma": hp.uniform("svr_gamma", 0, 10),
                "epsilon": hp.uniform("svr_epsilon", 0, 10),
                "kernel": hp.choice("svr_kernel", ["rbf", "linear"]),
            },
        },
        {
            "algo": DecisionTreeRegressor,
            "kwargs": {
                "criterion": hp.choice("dt_criterion", ["mse", "friedman_mse", "mae"]),
                "max_depth": hp.choice("dt_max_depth", [None, hp.randint("max_depth_int", 1, 3)])
            },
        },
        {
            "algo": XGBRegressor,
            "kwargs": {
                "n_estimators": hp.randint("xgb_n_estimators", 50, 500),
                "learning_rate": hp.uniform("xgb_learning_rate", 0, 1),
                "objective": hp.choice("xgb_objective", ["reg:squarederror", "reg:squaredlogerror"]),
                # "booster": hp.choice("xgb_booster", ["gbtree", "dart"]),
                # "gamma": hp.uniform("xgb_gamma", 0, 0.5),
                # "reg_alpha": hp.uniform("xgb_reg_alpha", 0, 0.5),
                # "reg_lambda": hp.uniform("xgb_reg_lambda", 0.5, 1),
                "max_depth": hp.randint("xgb_max_depth", 2, 6),
                "verbosity": 0,
            }
        },
        {
            "algo": LGBMRegressor,
            "kwargs": {
                "n_estimators": hp.randint("lgb_n_estimators", 50, 500),
                "learning_rate": hp.uniform("lgb_learning_rate", 0, 1),
                "boosting_type": hp.choice("lgb_boosting_type", ["gbdt", "dart"]),
                # "boosting_type": hp.choice("lgb_boosting_type", ["gbdt", "dart", "goss"]),
                "max_depth": hp.randint("lgb_max_depth", 2, 6),
                # "num_leaves": hp.randint("lgb_num_leaves", 5, 70),
                # "reg_alpha": hp.uniform("lgb_reg_alpha", 0, 1),
                # "reg_lambda": hp.uniform("lgb_reg_lambda", 0, 1),
                "silent": True,
                "verbose": -1,
            }
        },
        {
            "algo": CatBoostRegressor,
            "kwargs": {
                "learning_rate": hp.uniform("cat_learning_rate", 0, 0.3),
                "max_depth": hp.randint("cat_max_depth", 3, 6),
                "verbose": False,
                "iterations": 100
            }
        }
    ])

    hpfeature_reg = {
        "algorithms": regression,
    }