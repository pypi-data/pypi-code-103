
from ..validates import Validate
from ..configs.pyod_config import hp_outlier_config
from ..data import DataObject
from hyperopt import fmin, tpe, STATUS_OK, hp
import numpy as np
import pandas as pd

class HpOuterlierDetect(object):
    
    def __init__(self, rounds=100, verbose=False):
        self.trials = []
        self.metrics = []
        self.rounds = rounds
        self.verbose = verbose
        self.summary = []

    def fit(self, algorithm, dataobject, cv=5):
        space = hp_outlier_config
        def f(params):
            outlier_algo = params["outlier_algo"]
            contamination = params["contamination"]
            if self.verbose:
                print(f"{outlier_algo.__name__}, contamination {round(contamination, 3)}")
            outlier_model = outlier_algo(contamination=contamination)
            outlier_model.fit(dataobject.X)
            preds = outlier_model.labels_
            new_x = dataobject.X[(preds-1).astype(bool)]
            new_y = dataobject.Y[(preds-1).astype(bool)]
            v = Validate(algorithm, DataObject(X=new_x, Y=new_y)).validate_switch(cv)
            error = v["rmse"]
            self.summary.append([outlier_algo.__name__, outlier_algo, contamination, v["r2_score"], v["rmse"]])
            self.metrics.append([error])
            self.trials.append([outlier_algo, contamination])
            return {"loss": error, "status": STATUS_OK}
        best = fmin(fn=f, space=space, algo=tpe.suggest, max_evals=self.rounds, verbose=self.verbose)
        self.metrics = np.array(self.metrics)
        self.best_metrics = self.metrics[self.metrics[:, 0] == self.metrics[:, 0].min()]
        best_i = np.argmin(self.metrics[:, 0])
        self.best_params = self.trials[best_i]
        self.summary = pd.DataFrame(self.summary, columns=["outlier", "outlier_obj", "contamination",
                                                           "r2", "rmse"])
        return self