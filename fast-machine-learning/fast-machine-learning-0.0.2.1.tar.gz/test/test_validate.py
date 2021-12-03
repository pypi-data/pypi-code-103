
import sys, numpy as np
sys.path.append("..")
from fml.preprocessing import Preprocessing
from fml.data import read_data
from fml.validates import Validate
from xgboost import XGBRegressor
algo = XGBRegressor

dataset = read_data("data.txt", df=False)
dataset = Preprocessing(corr_criterion=0.90).fit_transform(dataset)

v = Validate(algo, dataset, dataset)
# v.validate_all()
# v.validate_train()
v.validate_switch(20)
v.validate_test()
v.validate_train()
v.validate_cv5()
v.validate_loo()
results = v.results
