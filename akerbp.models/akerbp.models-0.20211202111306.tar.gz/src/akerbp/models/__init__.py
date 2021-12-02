import os
import joblib
import importlib
import pandas as pd

from importlib.metadata import version
try:
    __version__ = version('akerbp.models')
except:
   __version__ = 'unknown' 

class Model():
    """    
    The main class to define a model

    Attributes
    ----------
        settings: dict
            the required keys for the dictionary:
                arbitrary model name: dict containing following keys (dict):
                    'model_parameters': dict of parameters required by xgboost.XGBRFClassifier (dict),
                    'use_class_weights': whether to use class weights in the model (boolean)
        model_path: str
            - If model_path is a path/to/dir/ then the serialized model is assumed to be (or will be saved to) 
            path/to/dir/model.joblib, and the labedl encoder at /path/to/dir/le.joblib
            - If model_path is a full/path/to/my_model.joblib,
            then the label encoder is saved (or assumed to be) at /full/path/to/my_model_le.joblib

    Methods
    -------
        predict(X:dict/pandas.DataFrame)

        evaluate(X_test:pandas.DataFrame, y_test:pandas.DataFrame, metrics:list, label_map:dict, **kwargs)

        save(model_path:str)
    """
    def __init__(self, settings, model_path, load=True):
        self.settings = settings
        for key, val in settings.items():
            setattr(self, key, val)

        self.model_path = model_path
        self._handle_model_path()

        if load:
            try:
                self.model = joblib.load(self.model_file_path)
                print('Model successfully loaded from ', self.model_file_path)
                self.le = joblib.load(self.le_file_path)
                print('LabelEncoder successfully loaded from ', self.le_file_path)
            except Exception as e:
                print('Cannot load the model - ', e)

    def _handle_model_path(self):
        if os.path.isfile(self.model_path):
            self.model_file_path = self.model_path
        else:
            if not os.path.isdir(self.model_path):
                os.makedirs(self.model_path)
            self.model_file_path = os.path.join(self.model_path, 'model.joblib')
        self.le_file_path = self.model_file_path.replace('.joblib', '_le.joblib')

    def predict(self, X, **kwarg):
        """
        Parameters
        ----------
            X: dict or pandas DataFrame with expected features

        Returns
        -------
            y: numpy array with predicted classes
        """
        if not hasattr(self, 'model'):
            raise ValueError('Model must be trained or loaded from file before predict can be run')
        self.X_pred = X
        self._validate_x_pred()

        if hasattr(self, '_validate_features'):
            self._validate_features()
        #FIXME! To fix the error that xgboost started throwing on both curve patching and badlog. investigate more?
        feats = self.model.get_booster().feature_names
        predictions = self.model.predict(self.X_pred[feats])
        if hasattr(self, 'le'):
            return self.le.inverse_transform(predictions)
        else:
            return predictions

    def _validate_x_pred(self):
        if isinstance(self.X_pred, dict):
            self.X_pred = pd.DataFrame.from_dict(self.X_pred)
        elif isinstance(self.X_pred, pd.core.frame.DataFrame):
            self.X_pred = self.X_pred
        else:
            raise ValueError('Please pass the data as a dict or a pandas DataFrame')


    def evaluate(self, X_test, y_test, metrics=None, label_map=None, **kwargs):
        """
        Evaluates the metrics for the test data

        Parameters
        ----------
        X_test: pandas DataFrame - raw features
        y_test: pandas DataFrame - correct labels
        metrics(optional): list - evaluation metrics you want calculated from the methods available at sklearn.metrics
            if no list is provided, the metrics list from the settings is used
        label_map(optional): dict - mapping the test set labels to another set, e.g. for metrics with this option
        **kwargs: arbitrary arguments that the expected metrics may need
        """
        if metrics is not None:
            self.metrics = metrics
        self.scores = dict()
        for metric in self.metrics:
            module_name = 'sklearn.metrics'
            cls_name = metric
            try:
                cls = getattr(importlib.import_module(module_name), cls_name)
            except AttributeError as ae:
                print(ae)
            else:
                y_pred = pd.DataFrame()
                y_pred['true'] = pd.to_numeric(y_test)
                y_pred['pred'] = pd.to_numeric(self.predict(X=X_test))
                if label_map is not None:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
                    y_pred['pred'] = y_pred['pred'].map(label_map)
                    y_pred['true'] = y_pred['true'].map(label_map)                    
                score = cls(y_pred['true'], y_pred['pred'], **kwargs)
                setattr(self, metric, score)
            self.scores[metric] = getattr(self, metric)
        return self.scores

    def save(self, model_path=None):
        if model_path is not None:
            self.model_path = model_path            

        self._handle_model_path()
        joblib.dump(self.model, self.model_file_path)
        print('Model successfully saved to {}'.format(self.model_file_path))
        joblib.dump(self.le, self.le_file_path)
        print('LabelEncoder successfully saved to {}'.format(self.le_file_path))
        return model_path