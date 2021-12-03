
import sys, numpy as np
sys.path.append("..")
from fml.preprocessing import Preprocessing
from fml.data import read_data
from fml.sampling.sphere_exclusion import random_split
from fml.sampling.hpsplit import HpSplit
from fml.configs.auto_config import AutoConfig
from fml.validates import Validate
from hyperopt import tpe, fmin, STATUS_OK
from fml.preprocessing import Preprocessing
from sklearn.datasets import load_boston, load_diabetes
from fml.data import DataObject
from fml.feature_selection import MRMR, Shap
from xgboost import XGBRegressor

dataset = read_data("Tc_filled.csv", df=False)
a = dataset.to_df()
dataset = Preprocessing().fit_transform(dataset)
b = dataset.to_df()

m = MRMR().fit_transform(dataset, max_f=10)
# m = Shap().fit_transform(XGBRegressor, dataset, max_f=5)
c = m.to_df()
