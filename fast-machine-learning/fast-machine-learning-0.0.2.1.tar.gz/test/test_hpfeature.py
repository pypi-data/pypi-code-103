
import sys, numpy as np
sys.path.append("..")
from fml.data import read_data
from fml.preprocessing import Preprocessing
from fml.sampling.sphere_exclusion import random_split
from fml.pipelines import HpFeatureParams
from fml.pipelines._utils import choose_feature_selection

trainset = read_data("train_5460.xlsx", df=False)
trainset_ = trainset.to_df()
testset = read_data("test_5460.xlsx", df=False)
testset_ = testset.to_df()

hpf = HpFeatureParams(verbose=True).fit(trainset, testset, max_f=10)
print(hpf.best_metrics)
best_p = hpf.best_params

feature_selection_method = choose_feature_selection(best_p["algorithms"]["algo"])
fsm = feature_selection_method().fit(best_p["algorithms"]["algo"], trainset, testset, **best_p["algorithms"]["kwargs"])
results = fsm.validate_all()
