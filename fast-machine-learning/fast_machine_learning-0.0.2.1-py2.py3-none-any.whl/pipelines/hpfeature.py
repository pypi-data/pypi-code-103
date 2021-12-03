
from hyperopt import fmin, tpe, STATUS_OK, hp
from ..configs.auto_config import AutoConfig
from ._utils import raise_dataobject as rd
import numpy as np, pandas as pd
from ._utils import choose_feature_selection

class HpFeature(object):

    def __init__(self, rounds=100, verbose=False):
        self.trials = []
        self.metrics = []
        self.rounds = rounds
        self.verbose = verbose
        self.summary = []

    def fit(self, trainobject, testobject, cv=5, min_f=3, max_f=5, task="reg"):
        """
        cv : 5, 10, True, False
        """
        rd(trainobject)
        rd(testobject)
        if task == "reg":
            space = AutoConfig().feature_selection
        else:
            raise Exception("cls not completed yet")
        space.update({
            "max_f": hp.randint("max_f", min_f, max_f),
            })
        def f(params):
            if self.verbose:
                print(params)
            (algo, model_p), = params["algorithms"].items()
            max_f = params["max_f"]
            feature_selection_method = choose_feature_selection(algo)
            fsm = feature_selection_method().fit(algo, trainobject, testobject, **model_p)
            try:
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
            except:
                error = 9999
                train_R2 = train_loss = test_R2 = test_loss = -1
            self.metrics.append([error, train_R2, train_loss, test_R2, test_loss])
            self.trials.append(params)
            self.summary.append(
                [max_f, algo.__name__, train_R2, train_loss, test_R2, test_loss, error])
            return {"loss": error, "status": STATUS_OK}
        best = fmin(fn=f, space=space, algo=tpe.suggest, max_evals=self.rounds, verbose=self.verbose)
        self.metrics = np.array(self.metrics)
        self.best_metrics = self.metrics[self.metrics[:, 0] == self.metrics[:, 0].min()]
        best_i = np.argmin(self.metrics[:, 0])
        self.best_params = self.trials[best_i]
        self.summary = pd.DataFrame(self.summary, columns=["max_f", "model_p", "train_R2",
                                                           "train_RMSE", "test_R2", "test_RMSE", "error"])
        return self
