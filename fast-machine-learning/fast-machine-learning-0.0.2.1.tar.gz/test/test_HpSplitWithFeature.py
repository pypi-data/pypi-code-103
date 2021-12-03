
import sys, numpy as np
sys.path.append("..")
from fml.data import read_data
from fml.preprocessing import Preprocessing
from fml.sampling import HpSplit, HpSplitWithFeature
from fml.pipelines import SHAPModelling
from fml.sampling.sphere_exclusion import random_split

dataset = read_data("zsldata_0802.xlsx", df=False)
print(dataset.X.shape)
dataset = Preprocessing(corr=False).fit_transform(dataset)
print(dataset.X.shape)
train, test = random_split(dataset, 0.1944, 5460)

# hswf = HpSplitWithFeature(verbose=True).fit(dataset, cv=5, max_f=26)
# print(hswf.best_metrics)
# best_p = hswf.best_params
# print(best_p)

# train, test = random_split(dataset, best_p["test_size"], best_p["random_state"])
# (algo, params), = best_p["algorithms"].items()
# shapm = SHAPModelling().fit(algo, train, test, **params)
# result = shapm.validate_all(max_f=best_p["max_f"])

train.to_df().to_excel("train_5460_nocorr.xlsx")
test.to_df().to_excel("test_5460_nocorr.xlsx")

# train_5 = shapm.feature_selection.transform(shapm.trainobject.copy(), best_p["max_f"])
# test_5 = shapm.feature_selection.transform(shapm.testobject.copy(), best_p["max_f"])
# train_5.to_df().to_excel("train_filter5_5460.xlsx")
# test_5.to_df().to_excel("test_filter5_5460.xlsx")
