
from ..feature_selection import MRMR, Shap
from ..validates import Validate
from sklearn.preprocessing import StandardScaler

class PipeLine(object):
    
    def __init__(self):
        self.feature_selection = None
        self.algo = None
        self.scaler = None

    def validate(self, cv=5, max_f=5):
        trainobject = self.feature_selection.transform(self.trainobject.copy(), max_f)
        testobject = self.feature_selection.transform(self.testobject.copy(), max_f)
        v = Validate(self.algo, trainobject, testobject, **self.model_p)
        return v.validate_switch(cv)

    def validate_all(self, max_f=5):
        trainobject = self.feature_selection.transform(self.trainobject.copy(), max_f)
        testobject = self.feature_selection.transform(self.testobject.copy(), max_f)
        v = Validate(self.algo, trainobject, testobject, **self.model_p).validate_all()
        return v.results
    
    def transform(self, max_f=5):
        trainobject = self.feature_selection.transform(self.trainobject.copy(), max_f)
        testobject = self.feature_selection.transform(self.testobject.copy(), max_f)
        return trainobject, testobject

class MRMRModelling(PipeLine):

    def fit(self, algo, trainobject, testobject, retrain=True, **model_p):
        trainobject_copy = trainobject.copy()
        testobject_copy = testobject.copy()
        if retrain or self.feature_selection is None:
            self.scaler = StandardScaler().fit(trainobject.X)
            trainobject_copy.X = self.scaler.transform(trainobject_copy.X)
            testobject_copy.X = self.scaler.transform(testobject_copy.X)
            self.feature_selection = MRMR().fit(trainobject_copy)
        self.trainobject = trainobject_copy
        self.testobject = testobject_copy
        self.algo = algo
        self.model_p = model_p
        return self

class SHAPModelling(PipeLine):

    def fit(self, algo, trainobject, testobject, retrain=True, **model_p):
        trainobject_copy = trainobject.copy()
        testobject_copy = testobject.copy()
        if retrain or self.feature_selection is None:
            self.feature_selection = Shap().fit(algo, trainobject_copy, model_kwargs=model_p)
        self.trainobject = trainobject_copy
        self.testobject = testobject_copy
        self.algo = algo
        self.model_p = model_p
        return self

