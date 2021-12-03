
from ..validates import Validate
from .sphere_exclusion import random_split
from hyperopt import fmin, tpe, STATUS_OK, Trials
from ..configs.auto_config import AutoConfig
from ._utils import raise_dataobject as rd
import numpy as np
from ._utils import choose_feature_selection
from ..pipelines import MRMRModelling, SHAPModelling
from ..feature_selection import Shap
from hyperopt import hp
import pandas as pd

class HpSplit(object):

    def __init__(self, rounds=100, verbose=False):
        self.trials = []
        self.metrics = []
        self.rounds = rounds
        self.verbose = verbose
        self.summary = []

    def fit(self, dataobject, cv=5):
        """
        cv : 5, 10, True, False
        """
        rd(dataobject)
        space = AutoConfig().split_data
        def f(params):
            if self.verbose:
                print(params)
            (algo, model_p), = params["algorithms"].items()
            test_size = params["test_size"]
            random_state = params["random_state"]
            trainset, testset = random_split(dataobject, test_size, random_state)
            v = Validate(algo, trainset, testset, **model_p)
            train = v.validate_switch(cv)
            train_loss = train["rmse"]
            train_R2 = train["r2_score"]
            test = v.validate_switch("test")
            test_loss = test["rmse"]
            test_R2 = test["r2_score"]
            if train_loss > test_loss or test_R2 < 0.6:
                error = train_loss*1.1
            else:
                error = train_loss
            self.metrics.append([error, train_R2, train_loss, test_R2, test_loss])
            self.trials.append(params)
            self.summary.append([test_size, random_state, algo.__name__, train_R2, train_loss, test_R2, test_loss, error])
            return {"loss": error, "status": STATUS_OK}
        best = fmin(fn=f, space=space, algo=tpe.suggest, max_evals=self.rounds, verbose=self.verbose)
        self.metrics = np.array(self.metrics)
        self.best_metrics = self.metrics[self.metrics[:, 0] == self.metrics[:, 0].min()]
        best_i = np.argmin(self.metrics[:, 0])
        self.best_params = self.trials[best_i]
        self.summary = pd.DataFrame(self.summary, columns=["test_size", "random_state", "algo", "train_R2",
                                                           "train_RMSE", "test_R2", "test_RMSE", "error"])
        return self

class HpSplitWithFeature(object):

    def __init__(self, rounds=100, verbose=False, fittedon="train"):
        self.trials = []
        self.metrics = []
        self.rounds = rounds
        self.verbose = verbose
        self.fittedon = fittedon
        self.summary = []

    def fit(self, dataobject, cv=5, min_f=3, max_f=5):
        """
        cv : 5, 10, True, False
        """
        rd(dataobject)
        space = AutoConfig().split_data
        space.update({
            "max_f": hp.randint("max_f", min_f, max_f),
            })
        def f(params):
            if self.verbose:
                print(params)
            (algo, model_p), = params["algorithms"].items()
            test_size = params["test_size"]
            random_state = params["random_state"]
            max_f = params["max_f"]
            trainset, testset = random_split(dataobject, test_size, random_state)
            feature_selection_method = choose_feature_selection(algo)
            fsm = feature_selection_method().fit(algo, trainset, testset, **model_p)
            # if self.fittedon == "train":
            #     if feature_selection_method == Shap:
            #         fsm = SHAPModelling().fit(algo, trainset, testset, **model_p)
            #     else:
            #         fsm = MRMRModelling().fit(algo, trainset, testset, **model_p)
            # else:
            #     if feature_selection_method == Shap:
            #         fsm = feature_selection_method().fit(algo, dataobject)
            #     else:
            #         fsm = feature_selection_method().fit(dataobject)
            train = fsm.validate(cv, max_f)
            train_loss = train["rmse"]
            train_R2 = train["r2_score"]
            test = fsm.validate("test", max_f)
            test_loss = test["rmse"]
            test_R2 = test["r2_score"]
            if train_loss > test_loss or test_R2 < 0.6:
                error = train_loss*1.1
            else:
                error = train_loss
            self.metrics.append([error, train_R2, train_loss, test_R2, test_loss])
            self.trials.append(params)
            self.summary.append([max_f, test_size, random_state, algo.__name__, train_R2, train_loss, test_R2, test_loss, error])
            return {"loss": error, "status": STATUS_OK}
        best = fmin(fn=f, space=space, algo=tpe.suggest, max_evals=self.rounds, verbose=self.verbose)
        self.metrics = np.array(self.metrics)
        self.best_metrics = self.metrics[self.metrics[:, 0] == self.metrics[:, 0].min()]
        best_i = np.argmin(self.metrics[:, 0])
        self.best_params = self.trials[best_i]
        self.summary = pd.DataFrame(self.summary, columns=["max_f", "test_size", "random_state", "algo", "train_R2",
                                                           "train_RMSE", "test_R2", "test_RMSE", "error"])
        return self