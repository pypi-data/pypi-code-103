
import sys, numpy as np
sys.path.append("..")
from fml.preprocessing import Preprocessing
from fml.data import read_data
from fml.sampling.sphere_exclusion import random_split
from fml.sampling.hpsplit import HpSplit, HpSplitWithFeature
from fml.configs.auto_config import AutoConfig
from fml.validates import Validate
from hyperopt import tpe, fmin, STATUS_OK
from fml.preprocessing import Preprocessing
from sklearn.datasets import load_boston, load_diabetes
from fml.data import DataObject
from fml.feature_selection import MRMR, Shap
from fml.sampling._utils import choose_feature_selection

# X, Y = load_boston(return_X_y=True)
# dataset = DataObject(X, Y)
dataset = read_data("Tc_filled.csv", df=False)
a = dataset.to_df()
dataset = Preprocessing().fit_transform(dataset)
# trainset, testset = random_split(dataset, 0.2, 0)
# a = trainset.to_df()
# b = testset.to_df()

hs = HpSplit(verbose=True).fit(dataset, cv=5)
print(hs.best_metrics)
best_p = hs.best_params
trainset, testset = random_split(dataset, best_p["test_size"], best_p["random_state"])
(algo, model_p), = best_p["algorithms"].items()
result = Validate(algo, trainset, testset, **model_p).validate_all().results

# =============================================================================
# hs = HpSplitWithFeature(verbose=True)
# hs.fit(dataset, cv=5, max_f=21)
# hs.best_metrics
# 
# best_p = hs.best_params
# trainset, testset = random_split(dataset, best_p["test_size"], best_p["random_state"])
# base_result = Validate(best_p["algorithms"], trainset, testset).validate_all().results
# fms = choose_feature_selection(best_p["algorithms"])
# if fms == Shap:
#     fms = Shap().fit(best_p["algorithms"], trainset)
# else:
#     fms = MRMR().fit(trainset)
# trainset = fms.transform(trainset, max_f=best_p["max_f"])
# testset = fms.transform(testset, max_f=best_p["max_f"])
# b = trainset.to_df()
# v = Validate(best_p["algorithms"], trainset, testset)
# v.validate_switch(5)
# v.validate_test()
# v.validate_loo()
# results = v.results
# =============================================================================

# space = AutoConfig().split_data
# verbose = True
# trials = []
# metrics = []
# rounds = 100
# def f(params):
#     algo = params["algorithms"]
#     test_size = params["test_size"]
#     random_state = params["random_state"]
#     trainset, testset = random_split(dataset, test_size, random_state)
#     v = Validate(algo, trainset, testset)
#     v.validate_switch(10)
#     v.validate_test()
#     train_loss = v.cv10_result["rmse"]
#     test_loss = v.test_result["rmse"]
#     if train_loss > test_loss:
#         error = train_loss + test_loss
#     else:
#         error = train_loss
#     metrics.append([error, train_loss, test_loss])
#     trials.append(params)
#     return {"loss": error, "status": STATUS_OK}
# fmin(fn=f, space=space, algo=tpe.suggest, max_evals=rounds, verbose=verbose)
# metrics = np.array(metrics)
# best_metrics = metrics[metrics[:, 0] == metrics[:, 0].min()]
# best_i = np.argmin(metrics[:, 0])
# best_params = trials[best_i]