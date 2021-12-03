from ..data import DataObject as DATA
from .feature_selection_model_fitting import MRMRModelling, SHAPModelling
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, \
    GradientBoostingClassifier, GradientBoostingRegressor
from catboost import CatBoostClassifier, CatBoostRegressor

def raise_dataobject(dataobject):
    if not isinstance(dataobject, DATA):
        raise Exception(f"not an {DATA}")
    dataobject.check()
    return dataobject

shap_list = [
    XGBRegressor, XGBClassifier,
    RandomForestRegressor, RandomForestClassifier,
    GradientBoostingClassifier, GradientBoostingRegressor,
    LGBMRegressor, LGBMClassifier,
    CatBoostClassifier, CatBoostRegressor
]

def choose_feature_selection(algo):
    if algo in shap_list:
        return SHAPModelling
    else:
        return MRMRModelling
