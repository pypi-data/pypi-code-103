
import sys, numpy as np
sys.path.append("..")
from fml.pipelines import MRMRModelling, SHAPModelling
from fml.data import read_data
from fml.preprocessing import Preprocessing
from fml.sampling import random_split
from sklearn.svm import SVR
from xgboost import XGBRegressor

dataset = read_data("zsldata_0802.xlsx", df=False)
print(dataset.X.shape)
dataset = Preprocessing().fit_transform(dataset)
print(dataset.X.shape)

trainobject, testobject = random_split(dataset, 0.20)


feature_selection = SHAPModelling().fit(XGBRegressor, trainobject, testobject)

for i in range(3, 26):
    loo = feature_selection.validate(cv=True, max_f=i)
    test = feature_selection.validate(cv="test", max_f=i)
    print(f"loo: {loo['r2_score']}")
    print(f"test: {test['r2_score']}")

