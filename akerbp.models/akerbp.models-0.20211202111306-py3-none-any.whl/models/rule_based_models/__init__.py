import os
import joblib
import pandas as pd
import importlib

from mlpet.Datasets import lithology
from akerbp.models import Model
from akerbp.models import classification_models
from akerbp.models.rule_based_models import helpers

class BadlogModel(Model):
    def __init__(self, **kwargs):
        """
        Initializes badlog model
        """
        self.kwargs = kwargs
        for key, val in kwargs.items():
            setattr(self, key, val)
        
    def _validate_input(self, X, **kwargs):
        if isinstance(X, dict):
            if 'metadata' not in X.keys():
                raise ValueError('"metadata" key is required')
            if 'data' not in X.keys():
                raise ValueError('"data" key is required')
            X_df = pd.DataFrame.from_dict(X['data'])
            metadata = X['metadata']
            self.X_pred, self.num_cols, self.cat_cols = helpers._apply_metadata(
                X_df, **kwargs.get('_metadata', metadata)
            )
        elif isinstance(X, pd.core.frame.DataFrame):
            X_df = X.copy()
            self.X_pred, self.num_cols, self.cat_cols = helpers._apply_metadata(
                X_df, **kwargs.get('_metadata', {})
            )
        else:
            raise ValueError('Please pass the data as a dict or a pandas DataFrame')

    def _init_cp_models(self, cp_names, folder_path, data_settings, model_settings, mappings):
        """
        Instantiate datasets and models for each of the crossplots

        Args:
            cp_names (list): list with crossplot names
            folder_path (str): path to folder with models
            data_settings (dict): settings of preprocessing for using the model
            model_settings (dict): settings of model XGBoost
            mappings (dict): mappings dictionary of cat variables

        Returns:
            tuple: dictionaries with dataset objects, models and key wells
        """
        datasets = dict()
        models = dict()
        key_wells = dict()
        folder_paths = dict()

        for cp_name in cp_names:
            print('init ds and model - BadlogModel - {}'.format(cp_name))
            folder_paths[cp_name] = os.path.join(folder_path, cp_name)
            datasets[cp_name] = lithology.Lithologydata(
                settings=data_settings, 
                mappings=mappings,
                folder_path=folder_paths[cp_name]
            ) #but don't load any data into the dataset, because we need to get that from running the find_crossplot_scores
            
            models[cp_name] = classification_models.XGBoostClassificationModel(
                model_settings, 
                folder_paths[cp_name]
            )

            key_wells[cp_name] = joblib.load(
                os.path.join(folder_paths[cp_name], 'key_wells.joblib')
            )
        return datasets, models, key_wells

    def _get_cp_params(self, **kwargs):
        """
        Returns necessary variables to generate crossplots predictions

        Returns:
            tuple: path to models folder, settings for data and models, mappings dictionary
        """
        settings = kwargs.get('settings', None)
        mappings = kwargs.get('mappings', None)
        folder_path = kwargs.get('folder_path', None)
        #Assuming all cp_names use the same model- and data-settings
        if all([settings, mappings, folder_path]):
            model_settings = settings['models']
            data_settings = settings['datasets']['lithology']
        else:
            raise ValueError(
                'Please provide settings, mappings and folder path for the crossplot method.'
            )
        return folder_path, data_settings, model_settings, mappings


    def predict(self, X, methods, **kwargs):
        """
        Args:
            X (dict or pd.DataFrame): expected features
            methods (list): list of methods to apply on X

        Returns:
            y (pd.DataFrame): including different badlog flags and scores
        """
        self._validate_input(X, **kwargs)

        #Validate feature
        self.X_pred = helpers._create_features(self.X_pred)

        self.X_pred_features = set(self.X_pred.columns)
        self.expected_curves = set([
            'DEPTH', 'DEN', 'DENC', 'AC', 'ACS', 'BS', 'CALI', 'GR',
            'NEU', 'RDEP', 'RMED', 'RMIC', 'PEF', 'GROUP'
        ])
        helpers._validate_features(self.X_pred_features, self.expected_curves)

        self.methods = methods
        self.y = pd.DataFrame()

        for method in self.methods:
            #Evaluate method
            method_helpers = importlib.import_module(
                'akerbp.models.rule_based_models.{}_helpers'.format(method)
            )
            method_evaluator = getattr(method_helpers, 'flag_{}'.format(method))
            if method == 'crossplot':
                cp_names = kwargs.get('cp_names', ['vp_den', 'vp_vs', 'ai_vpvs'])
                datasets, models, key_wells = self._init_cp_models(
                    cp_names, *self._get_cp_params(**kwargs)
                )
                method_flags = method_evaluator(
                    self.X_pred, cp_names, datasets, models, key_wells
                )
            else:
                method_flags = method_evaluator(self.X_pred)
            self.y[method_flags.columns] = method_flags
        result_columns = [col for col in self.y.columns if col.split('_')[0] in ['flag', 'agg', 'score']]
        return self.y[result_columns]