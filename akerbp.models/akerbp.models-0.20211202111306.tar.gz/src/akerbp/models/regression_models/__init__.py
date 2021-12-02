import os
import joblib
import xgboost
import pandas as pd

from akerbp.models import Model

class RegressionModel(Model):
    pass

class XGBoostRegressionModel():
    """    
    subclass of akerbp.model

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

        predict_proba(X:dict/pandas/DataFrame)

        train(df:pandas.DataFrame, targets:np.array)

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
            except:
                pass

    def _handle_model_path(self):
        if os.path.isfile(self.model_path):
            self.model_file_path = self.model_path
        else:
            if not os.path.isdir(self.model_path):
                os.makedirs(self.model_path)
            self.model_file_path = os.path.join(self.model_path, 'model.joblib')

    def _handle_model_path(self):
        if os.path.isfile(self.model_path):
            self.model_file_path = self.model_path
        else:
            if not os.path.isdir(self.model_path):
                os.makedirs(self.model_path)
            self.model_file_path = os.path.join(self.model_path, 'model.joblib')

    def _validate_features(self):
        # This function should be able to take in features in their
        # raw, unprocessed form as read from the file test.csv and
        # return predictions as an array integers of the same length
        if self.X_pred is None:
            return []

        #Check that the features in the model match the features provided in the data (including their order)
        self.model_features = self.model.get_booster().feature_names
        if sorted(self.model_features) != sorted(self.X_pred.columns.values):
            raise ValueError('Features in the provided dataset does not match the model expectation - Expected: {}, Provided: {}'.format(
        list(self.model_features), list(self.X_pred.columns)))
        self.X_pred = self.X_pred[self.model_features]

    def predict(self, X):
        """
        Parameters
        ----------
            X: dict or pandas DataFrame with expected features

        Returns
        -------
            y: numpy array with predicted classes
        """
        if isinstance(X, dict):
            self.X_pred = pd.DataFrame.from_dict(X)
        elif isinstance(X, pd.core.frame.DataFrame):
            self.X_pred = X
        else:
            raise ValueError('Please pass the data as a dict or a pandas DataFrame')
        self._validate_features()
        return self.model.predict(self.X_pred, validate_features=True)

    def predict_proba(self, X):
        """
        Not relevant for regression model
        """
        raise ValueError('predict_proba only relevant for classification models')

    def train(self, df, targets):
        ''' 
        Trains on the data given in the provided dataframe and targets. 
        The curves of the model must be present in the dataframe. 

        Parameters
        ----------
            df:         Pandas dataframe of features
            targets:    List of integers of the same length as the number of rows in df
        '''

        self.model = xgboost.XGBRegressor(**self.model_parameters)
        self.model.fit(df, targets)

    #FIXME!
    def explain(self):
        raise ValueError('Not implemented for this model')

    def evaluate(self, X_test, y_test, metrics=None, label_map=None, **kwargs):
        raise ValueError('Not implemented for this method')

    def save(self, model_path=None):
        if model_path is not None:
            self.model_path = model_path            

        self._handle_model_path()
        joblib.dump(self.model, self.model_file_path)
        print('Model successfully saved to {}'.format(self.model_file_path))
        return model_path

