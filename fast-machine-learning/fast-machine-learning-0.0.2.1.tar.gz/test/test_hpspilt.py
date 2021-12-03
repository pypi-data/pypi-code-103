
import sys, numpy as np
sys.path.append("..")
from fml.preprocessing import Preprocessing
from fml.data import read_data
from fml.sampling.sphere_exclusion import random_split
from fml.sampling.hpsplit import HpSplit, HpSplitWithFeature
from fml.configs.auto_config import AutoConfig
from fml.validates import Validate
from fml.preprocessing import Preprocessing
from sklearn.datasets import load_boston, load_diabetes
from fml.data import DataObject
from fml.feature_selection import MRMR, Shap
from fml.sampling._utils import choose_feature_selection
from xgboost import XGBRegressor

dataset = read_data("zsldata_prev.xlsx", df=False)
a = dataset.to_df()
dataset = Preprocessing().fit_transform(dataset)
a = dataset.to_df()

# hs = HpSplitWithFeature(verbose=True).fit(dataset, cv=5, max_f=15)
hs = HpSplit(verbose=True).fit(dataset, cv=5)
print(hs.best_metrics)
best_p = hs.best_params
trainset, testset = random_split(dataset, best_p["test_size"], best_p["random_state"])
(algo, model_p), = best_p["algorithms"].items()
result = Validate(algo, trainset, testset, **model_p).validate_all().results

