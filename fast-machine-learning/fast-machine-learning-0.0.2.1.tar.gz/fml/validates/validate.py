
from ._utils import raise_dataobject
from ..utils.base_func import metrics
from sklearn.model_selection import LeaveOneOut, KFold
import numpy as np

class Validate(object):

    def __init__(self, algo, TrainDataObject, TestDataObject=None, **modelparams):
        raise_dataobject(TrainDataObject)
        self.train = TrainDataObject
        if TestDataObject is None:
            self.test_f = False
        else:
            raise_dataobject(TrainDataObject)
            self.test = TestDataObject
            self.test_f = True
        self.modelparams = modelparams
        self.algo = algo

        self.train_result = None
        self.test_result = None
        self.loo_result = None
        self.cv10_result = None
        self.cv5_result = None

        self.additional_results = dict()

        self.metrics = metrics(algo)

    def validate_train(self):
        model_params = self.modelparams
        model = self.algo(**model_params).fit(self.train.X, self.train.Y)
        preds = model.predict(self.train.X)
        self.train_result = self.metrics(self.train.Y, preds)
        self.train_result.update(dict(model=model))
        return self

    def validate_test(self):
        if self.test_f:
            if self.train_result is None:
                self.validate_train()
            preds = self.train_result["model"].predict(self.test.X)
            self.test_result = self.metrics(self.test.Y, preds)
        else:
            raise Exception("No test data")
        return self

    def validate_cv10(self, shuffle=True):
        self.validate_cv(10, shuffle)
        return self

    def validate_cv5(self, shuffle=True):
        self.validate_cv(5, shuffle)
        return self

    def validate_cv(self, cv, shuffle=True):
        kf = KFold(n_splits=cv, shuffle=shuffle)
        model_params = self.modelparams
        X = self.train.X
        Y = self.train.Y
        kf.get_n_splits(X)
        preds = []
        obs = []
        for itrain, itest in kf.split(X):
            xtrain, xtest = X[itrain], X[itest]
            ytrain, ytest = Y[itrain], Y[itest]
            preds += self.algo(**model_params).fit(xtrain, ytrain).predict(xtest).tolist()
            obs += ytest.tolist()
        preds = np.array(preds)
        obs = np.array(obs)
        result = self.metrics(obs, preds)
        self.__dict__.update({
            f"cv{cv}_result": result
        })
        if cv not in [5, 10]:
            self.additional_results.update({
                f"cv{cv}": result
            })
        return self

    def validate_loo(self):
        model_params = self.modelparams
        loo = LeaveOneOut()
        X = self.train.X
        Y = self.train.Y
        loo.get_n_splits(X)
        preds = []
        obs = []
        for itrain, itest in loo.split(X):
            xtrain, xtest = X[itrain], X[itest]
            ytrain, ytest = Y[itrain], Y[itest]
            preds += self.algo(**model_params).fit(xtrain, ytrain).predict(xtest).tolist()
            obs += ytest.tolist()
        preds = np.array(preds)
        obs = np.array(obs)
        self.loo_result = self.metrics(obs, preds)
        return self

    def validate_all(self, additional_cv=[], shuffle=True):
        iter_list = [self.validate_train, self.validate_cv10, self.validate_cv5, self.validate_loo]
        if self.test_f:
            iter_list += [self.validate_test]
        iter_list += additional_cv
        for index, validate in enumerate(iter_list):
            if index >= 5:
                if isinstance(validate, int):
                    self.validate_cv(validate, shuffle)
            else:
                validate()
        return self

    def validate_switch(self, flag):
        if flag == True:
            self.validate_loo()
            return self.loo_result
        elif flag == False:
            self.validate_train()
            return self.train_result
        elif flag == "test":
            self.validate_test()
            return self.test_result
        elif isinstance(flag, int):
            self.validate_cv(flag)
            if flag == 5:
                return self.cv5_result
            elif flag == 10:
                return self.cv10_result
            else:
                return self.additional_results[f"cv{flag}"]
    @property
    def results(self):
        results_ = dict(
            train=self.train_result,
            test=self.test_result,
            loo=self.loo_result,
            cv5=self.cv5_result,
            cv10=self.cv10_result
            )
        results_.update(self.additional_results)
        return results_

