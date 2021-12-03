
from ..validates import Validate
from ..data import DataObject
from hyperopt import fmin, STATUS_OK, tpe, hp
import numpy as np
from sklearn.metrics import mean_squared_error
from ..utils.base_func import metrics
from ..data import DataObject
from shap.explainers import Permutation

# class VotingRegressor(object):
#
#     def __init__(self, algorithms, trainobjects, testobjects, model_ps=[], rounds=100, verbose=False):
#         self.algorithms = algorithms
#         self.trainobjects = trainobjects
#         self.testobjects = testobjects
#         self.model_ps = model_ps
#         self.externalobjects = []
#         self.estimators = []
#         self.weights = []
#         self.verbose = verbose
#         self.loo_preds = []
#         self.train_preds = []
#         self.test_preds = []
#         self.train_true_value = trainobjects[0].Y
#         self.test_true_value = testobjects[0].Y
#         self.trials = []
#         self.metrics = metrics(algorithms[0])
#         self.rounds = rounds
#         self.validates = []
#
#     def fit_models(self):
#         for algo, train, test, model_p in zip(self.algorithms, self.trainobjects, self.testobjects, self.model_ps):
#             v = Validate(algo, train, test, **model_p)
#             v.validate_all()
#             self.estimators.append(v.train_result["model"])
#             self.loo_preds.append(v.loo_result["preds"])
#             self.train_preds.append(v.train_result["preds"])
#             self.test_preds.append(v.test_result["preds"])
#             self.validates.append(v)
#         self.loo_preds = np.array(self.loo_preds)
#         self.train_preds = np.array(self.train_preds)
#         self.test_preds = np.array(self.test_preds)
#
#     def transform(self, externalobject):
#         self.externalobjects = []
#         df = externalobject.to_df()
#         for trainobject in self.trainobjects:
#             columns = trainobject.to_df().columns
#             tmp = df.loc[:, columns]
#             dataobject = DataObject().from_df(tmp)
#             self.externalobjects.append(dataobject)
#
#     def fit(self, fiton="test"):
#         self.trials
#         if len(self.estimators) == 0:
#             self.fit_models()
#         space = {}
#         weight_names = []
#         for index in range(len(self.algorithms)):
#             weight_name = f"w_{index}"
#             space.update({
#                 weight_name: hp.uniform(weight_name, 0.1, 0.99)
#             })
#             weight_names.append(weight_name)
#         def f(params):
#             if self.verbose:
#                 print(params)
#             weights = []
#             for weight_name in weight_names:
#                 weights.append(params[weight_name])
#             weights = np.array(weights)
#             weights = weights / weights.sum()
#             loo_preds = np.average(self.loo_preds, axis=0, weights=weights)
#             loo_error = (mean_squared_error(self.train_true_value, loo_preds)) ** 0.5
#             test_preds = np.average(self.test_preds, axis=0, weights=weights)
#             test_error = (mean_squared_error(self.test_true_value, test_preds)) ** 0.5
#             if fiton == "test":
#                 error = test_error
#             elif fiton == "loo":
#                 error = loo_error
#             elif fiton == "both":
#                 error = test_error + loo_error
#             self.trials.append([error] + weights.reshape(-1, ).tolist())
#             return {"loss": error, "status": STATUS_OK}
#         best = fmin(fn=f, space=space, algo=tpe.suggest, max_evals=self.rounds, verbose=self.verbose)
#         self.trials = np.array(self.trials)
#         self.best_trials = self.trials[self.trials[:, 0] == self.trials[:, 0].min()]
#         best_i = np.argmin(self.trials[:, 0])
#         self.best_weights = self.trials[best_i][1:]
#         return self
#
#     def results(self):
#         loo_preds = np.average(self.loo_preds, axis=0, weights=self.best_weights)
#         train_preds = np.average(self.train_preds, axis=0, weights=self.best_weights)
#         test_preds = np.average(self.test_preds, axis=0, weights=self.best_weights)
#         return {
#             "train": self.metrics(self.train_true_value, train_preds),
#             "loo": self.metrics(self.train_true_value, loo_preds),
#             "test": self.metrics(self.test_true_value, test_preds),
#         }
#
#     def predict(self, externelobject, weights=None):
#         self.transform(externelobject)
#         preds = []
#         for estimator, externelobject_ in zip(self.estimators, self.externalobjects):
#             pred = estimator.predict(externelobject_.X)
#             preds.append(pred.reshape(-1, ))
#         if weights is None:
#             weights = self.best_weights
#         preds = np.average(preds, axis=0, weights=weights)
#         return preds

class VotingRegressor(object):

    def __init__(self, weights=None, rounds=100, verbose=False, estimators=[]):

        self.weights = weights
        if self.weights is None:
            self.weights = np.array([1, 1, 1]) / np.array([1, 1, 1]).sum()
        self.rounds = rounds
        self.verbose = verbose

        self.estimators = estimators
        self.train_obs = []
        self.test_obs = []
        self.loo_obs = []
        self.loo_preds = []
        self.test_preds = []
        self.train_preds = []
        self.cv5_preds = []
        self.cv5_obs = []
        self.cv10_preds = []
        self.cv10_obs = []
        
        self.trainobjects = None

    def fit(self, algorithms, trainobjects, testobjects, model_parameters, fiton="test"):
        if len(self.estimators) == 0:
            self.fit_models(algorithms, trainobjects, testobjects, model_parameters)
        space = {}
        weight_names = []
        for index in range(len(algorithms)):
            weight_name = f"w_{index}"
            space.update({
                weight_name: hp.uniform(weight_name, 0.1, 0.99)
            })
            weight_names.append(weight_name)
        trials = []
        def f(params):
            if self.verbose:
                print(params)
            weights = []
            for weight_name in weight_names:
                weights.append(params[weight_name])
            weights = np.array(weights)
            weights = weights / weights.sum()
            loo_preds = np.average(self.loo_preds, axis=1, weights=weights)
            loo_error = (mean_squared_error(self.train_obs, loo_preds)) ** 0.5
            test_preds = np.average(self.test_preds, axis=1, weights=weights)
            test_error = (mean_squared_error(self.test_obs, test_preds)) ** 0.5
            if fiton == "test":
                error = test_error
            elif fiton == "loo":
                error = loo_error
            elif fiton == "both":
                error = test_error + loo_error
            trials.append([error] + weights.reshape(-1, ).tolist())
            return {"loss": error, "status": STATUS_OK}
        fmin(fn=f, space=space, algo=tpe.suggest, max_evals=self.rounds, verbose=self.verbose)
        trials = np.array(trials)
        self.best_trials = trials[trials[:, 0] == trials[:, 0].min()]
        best_i = np.argmin(trials[:, 0])
        self.best_weights = trials[best_i][1:]
        self.weights = self.best_weights
        self.trials = trials
        return self

    def fit_models(self, algorithms, trainobjects, testobjects, model_parameters):
        self.trainobjects = trainobjects
        for algorithm, trainobject, testobject, model_p in zip(algorithms, trainobjects, testobjects, model_parameters):
            v = Validate(algorithm, trainobject, testobject, **model_p)
            v.validate_train()
            v.validate_loo()
            v.validate_test()
            self.loo_preds.append(v.loo_result["preds"].reshape(-1, 1))
            self.test_preds.append(v.test_result["preds"].reshape(-1, 1))
            self.estimators.append(v.train_result["model"])
            self.train_preds.append(v.train_result["preds"].reshape(-1, 1))
        self.loo_preds = np.concatenate(self.loo_preds, axis=1)
        self.test_preds = np.concatenate(self.test_preds, axis=1)
        self.train_preds = np.concatenate(self.train_preds, axis=1)

        self.loo_obs = self.train_obs = trainobject.Y
        self.test_obs = testobject.Y

        from sklearn.model_selection import KFold
        for cv in [5, 10]:
            kf = KFold(n_splits=cv, shuffle=True)
            kf.get_n_splits(trainobjects[0].X)
            kf_preds = []
            kf_obs = []
            for itrain, itest in kf.split(trainobjects[0].X):
                kf_part_preds = []
                kf_part_obs = []
                for algorithm, trainobject, testobject, model_p in zip(algorithms, trainobjects, testobjects, model_parameters):
                    xtrain, xtest = trainobject.X[itrain], trainobject.X[itest]
                    ytrain, ytest = trainobject.Y[itrain], trainobject.Y[itest]
                    kf_part_preds.append(algorithm(**model_p).fit(xtrain, ytrain).predict(xtest).reshape(-1, 1))
                    kf_part_obs.append(ytest.reshape(-1, 1))
                kf_part_preds = np.concatenate(kf_part_preds, axis=1)
                kf_part_obs = np.concatenate(kf_part_obs, axis=1)
                kf_preds.append(kf_part_preds)
                kf_obs.append(kf_part_obs)
            if cv == 5:
                self.cv5_preds = np.concatenate(kf_preds, axis=0)
                self.cv5_obs = np.concatenate(kf_obs, axis=0)[:, 0]
            elif cv == 10:
                self.cv10_preds = np.concatenate(kf_preds, axis=0)
                self.cv10_obs = np.concatenate(kf_obs, axis=0)[:, 0]
        self.metrics = metrics(algorithms[0])

    @property
    def results(self):
        return_dict = {}
        for i, j, k in zip(["train", "loo", "test", "cv5", "cv10"],
                        [self.train_preds, self.loo_preds, self.test_preds, self.cv5_preds, self.cv10_preds],
                        [self.train_obs, self.loo_obs, self.test_obs, self.cv5_obs, self.cv10_obs]):
            preds = np.average(j, weights=self.weights, axis=1)
            return_dict.update({
                i: self.metrics(k, preds)
            })
        return return_dict

    def transform(self, externalobject):
        self.externalobjects = []
        df = externalobject.to_df()
        for trainobject in self.trainobjects:
            columns = trainobject.to_df().columns
            tmp = df.loc[:, columns]
            dataobject = DataObject().from_df(tmp)
            self.externalobjects.append(dataobject)

    def predict(self, externelobject, weights=None):
        self.transform(externelobject)
        preds = []
        for estimator, externelobject_ in zip(self.estimators, self.externalobjects):
            pred = estimator.predict(externelobject_.X).reshape(-1, 1)
            preds.append(pred)
        preds = np.concatenate(preds, axis=1)
        if weights is None:
            weights = self.weights
        preds = np.average(preds, axis=1, weights=weights)
        return preds

class VotingShap(object):
    
    def __init__(self, votingregressor, dataobject):
        self.votingregressor = votingregressor
        self.dataobject = dataobject
        self.columns = []
        self.columns_set = []
        self.define_columns()

    def define_columns(self):
        for trainobj in self.votingregressor.trainobjects:
            self.columns.append(trainobj.Xnames.tolist())
            self.columns_set += trainobj.Xnames.tolist()
        self.columns_set = list(set(self.columns_set))
        
        Y_name = str(self.votingregressor.trainobjects[0].Yname[0])
        
        if Y_name != self.dataobject.Yname:
            Y_name = self.dataobject.Yname

        self.columns_set = [Y_name] + self.columns_set
        data = self.dataobject.to_df().loc[:, self.columns_set]
        self.dataobject = DataObject().from_df(data)

    def predict(self, X):
        data = DataObject(X=X.values, Y=np.zeros(X.shape[0]), Xnames=X.columns,
                          Yname=self.votingregressor.trainobjects[0].Yname[0])
        predictions = self.votingregressor.predict(data)
        return predictions

    def fit(self):
        X = self.dataobject.to_df().iloc[:, 1:]
        explainer = Permutation(self.predict, X, feature_names=self.dataobject.Xnames)
        self.shap_values = explainer(X)
        self.feature_importance = self.shap_values.abs.mean(0).values
        if len(self.feature_importance.shape) > 1: self.feature_importance = self.feature_importance[:, 0]
        self.feature_shap = np.array(sorted(enumerate(self.feature_importance), key=lambda x: x[1], reverse=True))
        self.feature_importance = self.feature_shap[:, 1]
        self.feature_order = self.feature_shap[:, 0].astype(int)
        return self








