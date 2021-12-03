import os
import pandas as pd

from akerbp.models.classification_models import ClassificationModel
from akerbp.models.classification_models import XGBoostClassificationModel

class HierarchicalModel(ClassificationModel):
    def __init__(self, highlevel_settings, lowlevel_settings, folder_path, mapping):
        """ 
        A specific subclass of XGBoostClassificationModel that trains models in two levels, 
        the _highlevel_ model that is provided with categories of labels, 
        and the _lowlevel_ models that are a set of models trained on more details labels 
        (the number of lowlevel models equals the number of categories of the highlevel model)

        Attributes
        ----------
            - highlevel_settings: dict - setting for the high level model - see settings for the parent class
            - lowlevel_settings: dict - shared setting for low level models - see settings for the parent class
            * Note that there is only one setting (model parameters etc.) is provided for each level, 
            therefore the "num_class" argument is set based on the number of labels available in training data
            - folder_path: str
            - mapping: dict - how to map categories(high level labels) to detailed classes
                keys: categories (labels used in highlevel model)
                values: detailed classes (labels used in corresponding lowlevel models)

        Methods
        -------

        """
        self.cat2cls_mapping = mapping
        self.folder_path = folder_path
        self.highlevel_folder_path = os.path.join(self.folder_path, 'high_level')
        self.lowlevel_folder_path = os.path.join(self.folder_path, 'low_level')
        self.highlevel_model = XGBoostClassificationModel(highlevel_settings, self.highlevel_folder_path)
        self.lowlevel_models = dict()
        for lowlevel_name, _ in self.cat2cls_mapping.items():
            self.lowlevel_models[lowlevel_name] = XGBoostClassificationModel(
                settings=lowlevel_settings,
                model_path=os.path.join(self.lowlevel_folder_path, f'{lowlevel_name}'))

    def train(self, df, targets):
        print('Training the high level model')
        high_level_df, high_level_y = do_sth(df, targets, mapping1)
        self.highlevel_model.train(high_level_df, high_level_y)
        
        print('Training low level models')
        for model_label, lowlevel_model in self.lowlevel_models.items():
            low_level_df, low_level_y = do_sth(df, targets, mapping2, model_label)
            lowlevel_model.train(low_level_df, low_level_y)

    def predict(self, X):
        print('Predicting high level labels')
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Only pandas DataFrame is supported at the moment.")
        y = X.copy()
        y['high_level'] = self.highlevel_model.predict(X)
        print('Predicting low level labels')
        for model_label, lowlevel_model in self.lowlevel_models.items():
            print(model_label)
            filt = y['high_level']==model_label
            try:
                pred = lowlevel_model.predict(y.loc[filt, X.columns])
                y.loc[filt, 'low_level'] = pred
            except ValueError as ve:
                #Unseen labels problem is likely to arise for categories that are made of classes with too few samples
                print(ve)
        return y

    def save(self, folder_path=None):
        if folder_path is None:
            folder_path = self.folder_path

        self.highlevel_model.save(self.highlevel_folder_path)
        for model_label, lowlevel_model in self.lowlevel_models.items():
            full_model_path = os.path.join(self.lowlevel_folder_path, '{}'.format(model_label))
            lowlevel_model.save(full_model_path)
            print('model {} saved in {}'.format(model_label, full_model_path))
