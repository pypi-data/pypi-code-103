
from ..validates import Validate
import numpy as np
from ..data import DataObject

class StackingRegressor(object):
    
    def __init__(self, algorithms, last_algorithm, trainobjects, testobjects, algorithms_model_ps, last_algorithm_model_p,
                 rounds=100, verbose=False):
        self.algorithms = algorithms
        self.last_algorithm = last_algorithm
        self.trainobjects = trainobjects
        self.testobjects = testobjects
        self.algorithm_model_ps = algorithms_model_ps
        self.last_algorithm_model_p = last_algorithm_model_p
        self.rounds = rounds
        self.verbose = verbose
        self.train_obs = trainobjects[0].Y
        self.test_obs = testobjects[0].Y
        self.Yname = trainobjects[0].Yname

        self.validates = []
        self.train_preds = []
        self.test_preds = []
        self.pred_names = []
        self.estimators = []

    def fit_models(self):
        for algorithm, trainobject, testobject, model_p in zip(self.algorithms, self.trainobjects, self.testobjects, self.algorithms_model_ps):
            v = Validate(algorithm, trainobject, testobject, **model_p)
            v.validate_train()
            v.validate_test()
            self.validates.append(v)
            self.train_preds.append(v.train_result["preds"])
            self.test_preds.append(v.test_result["preds"])
            self.pred_names.append(f"{algorithm.__name__}+_pred")
            self.estimators.append(v.train_result["model"])
        self.train_preds = np.array(self.train_preds).reshape(trainobject.X.shape[0], -1)
        self.test_preds = np.array(self.test_preds).reshape(testobject.X.shape[0], -1)
        self.pred_names = np.array(self.pred_names)
        self.stacking_trainobject = DataObject(X=self.train_preds, Y=self.train_obs, Xnames=self.pred_names, Yname=self.Yname)
        self.stacking_testobject = DataObject(X=self.test_preds, Y=self.test_obs, Xnames=self.pred_names, Yname=self.Yname)

    def fit(self):
        if len(self.estimators) == 0:
            self.fit_models()
        self.stacking_v = Validate(self.last_algorithm, self.stacking_trainobject, self.stacking_testobject, **self.last_algorithm_model_p).validate_all()
        return self

    def results(self):
        return self.stacking_v.results

    def transform(self, externalobject):
        def transform(self, externalobject):
            self.externalobjects = []
            df = externalobject.to_df()
            for trainobject in self.trainobjects:
                columns = trainobject.to_df().columns
                tmp = df.loc[:, columns]
                dataobject = DataObject().from_df(tmp)
                self.externalobjects.append(dataobject)

    def predict(self, externelobject):
        self.transform(externelobject)
        preds = []
        for estimator, externelobject_ in zip(self.estimators, self.externalobjects):
            pred = estimator.predict(externelobject_.X)
            preds.append(pred.reshape(-1, ))
        preds = np.array(preds)
        preds = self.stacking_v.train_result["model"].predict(preds)
        return preds




