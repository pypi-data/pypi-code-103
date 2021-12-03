
from ._utils import choose_feature_selection
import pandas as pd, numpy as np
from ..configs.auto_config import reg_dict

metric_names = [
    "r2_score",
    "R",
    "rmse",
    "mae",
    "mse"
]
validate_names = [
    "train",
    "loo",
    "cv5",
    "cv10",
    "test"
]

summary_name = []
for validate_name in validate_names:
    for metric_name in metric_names:
        summary_name.append(f"{validate_name}_{metric_name}")

class RFA(object):

    def __init__(self, verbose=True):
        self.metrics = []
        self.summary = []
        self.metrics_all = []
        self.summary_all = []
        self.verbose = verbose

    def fit(self, algo, trainobject, testobject, min_f=3, max_f=21, **model_p):
        feature_selection_method = choose_feature_selection(algo)
        fsm = feature_selection_method().fit(algo, trainobject, testobject, **model_p)
        for num_f in range(min_f, max_f):
            results = fsm.validate_all(num_f)
            self.metrics.append([
                num_f,
                results["loo"]["r2_score"],
                results["loo"]["RMSE"],
                results["test"]["r2_score"],
                results["test"]["RMSE"]
            ])
            if self.verbose:
                print(
                    f"{algo.__name__}, num_f: {num_f}, loo_r2: {results['loo']['r2_score']}, test_r2: {results['test']['r2_score']}")
            summary_line = [num_f]
            for validate_name in validate_names:
                for metric_name in metric_names:
                    summary_line.append(results[validate_name][metric_name])
            self.summary.append(summary_line)
        self.metrics = np.array(self.metrics)
        self.best_metrics = self.metrics[self.metrics[:, 0] == self.metrics[:, 0].min()]
        self.metrics = pd.DataFrame(self.metrics, columns=["feature_num", "loo_r2_score", "loo_RMSE", "test_r2_score", "test_RMSE"])
        self.summary = pd.DataFrame(self.summary, columns=["feature_num"]+summary_name)
        return self

    def fit_all(self, trainobject, testobject, min_f=3, max_f=21):
        for reg_dict_ in reg_dict:
            for algo, model_p in reg_dict_.items():
                feature_selection_method = choose_feature_selection(algo)
                fsm = feature_selection_method().fit(algo, trainobject, testobject, **model_p)
                for num_f in range(min_f, max_f):
                    results = fsm.validate_all(num_f)
                    self.metrics_all.append([
                        algo.__name__,
                        num_f,
                        results["loo"]["r2_score"],
                        results["loo"]["rmse"],
                        results["test"]["r2_score"],
                        results["test"]["rmse"]
                    ])
                    if self.verbose:
                        print(
                            f"{algo.__name__}, num_f: {num_f}, loo_r2: {results['loo']['r2_score']}, test_r2: {results['test']['r2_score']}")
                    summary_line = [algo.__name__, num_f]
                    for validate_name in validate_names:
                        for metric_name in metric_names:
                            summary_line.append(results[validate_name][metric_name])
                    self.summary_all.append(summary_line)
        self.metrics_all = pd.DataFrame(self.metrics_all,
                                            columns=["algorithm", "feature_num", "loo_r2_score", "loo_RMSE", "test_r2_score", "test_RMSE"])
        self.summary_all = pd.DataFrame(self.summary_all, columns=["algorithm", "feature_num"]+summary_name)
        return self