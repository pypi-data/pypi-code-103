import os
import numpy as np

from akerbp.models.classification_models import ClassificationModel
from akerbp.models.classification_models import XGBoostClassificationModel

class NestedShaleModel(ClassificationModel):
    ''' A wrapper object for two models

        1. A model that predicts shale
        2. A model that predicts all classes except shale
    '''
    
    def __init__(self, shale_settings, other_settings, model_path):
        self.model_path = model_path
        self.shale_settings = shale_settings
        self.other_settings = other_settings
        self.shale_model = XGBoostClassificationModel(shale_settings, os.path.join(self.model_path, 'shale_model'))
        self.other_model = XGBoostClassificationModel(other_settings, os.path.join(self.model_path, 'other_model'))        
        self.label_shale = 65000

    def predict(self, X):
        if self.shale_model is None or self.other_model is None:
            raise ValueError('Model must be trained or loaded from file before predict can be run')
        shale_prediction = self.shale_model.predict(X)
        other_prediction = self.other_model.predict(X[shale_prediction == -1])
        full_prediction = np.zeros(X.shape[0])
        full_prediction[shale_prediction == self.label_shale] = self.label_shale
        full_prediction[shale_prediction == -1] = other_prediction
        return full_prediction.astype(int)

    def train(self, df, targets):
        # Train the binary shale classification model
        print('Training shale model..')
        targets_shale = np.copy(targets)
        targets_shale[targets_shale != self.label_shale] = -1 
        self.shale_model.train(df, targets_shale)
        print('Training model for non-shale lithologies..')
        targets_nonshale = targets[targets != self.label_shale].copy()
        df_nonshale = df[targets != self.label_shale]
        self.other_model.train(df_nonshale, targets_nonshale)

    def save(self, model_path=None):
        if model_path is None:
            model_path = self.model_path

        self.shale_model.save(model_path=os.path.join(self.model_path, 'shale_model'))
        self.other_model.save(model_path=os.path.join(self.model_path, 'other_model'))
