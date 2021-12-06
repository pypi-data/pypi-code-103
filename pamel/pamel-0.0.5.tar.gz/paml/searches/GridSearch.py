import copy
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import ParameterGrid
from sklearn.ensemble import RandomForestRegressor, AdaBoostClassifier, AdaBoostRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVR

from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor

from boruta import BorutaPy
from multiprocessing.dummy import Pool as ThreadPool

from paml.metrics import Metrics
from paml.searches import Base
from paml.searches import SearchSpaces
from paml.searches.wrapper_catboost import CatBoostClassifierScikit, CatBoostRegressorScikit

class GridSearch:
    '''GridSearch implements fit, get_best_model, get_best_model by KS (for classification only), predict (from the estimator) '''
    def __init__(self, task: str,
                 search_space: dict = None,
                 feature_selector_search_space=None,
                 models=['all'],
                 compute_ks: bool = False,
                 acceptance_rate: float = 0.01,
                 feature_selection: bool = False):

        self.search_space = search_space
        self.feature_selector_search_space = feature_selector_search_space
        self.models = models
        self.task = task
        self.compute_ks = compute_ks
        self.acceptance_rate = acceptance_rate
        self.feature_selection = feature_selection

        if self.task != 'classification' and self.compute_ks == True:
            raise BaseException(
                "You can't use compute_ks as True in this taks. Please set it to False")

        self.__set_model_params_grid__(
            self.search_space, self.models, self.task)

        if not self.feature_selector_search_space:
            self.feature_selector_search_space = [{'selector': [BorutaPy(estimator=RandomForestRegressor(n_jobs=-1))],
                                                   'max_depth': [5]}]

    def __set_model_params_grid__(self, search_space, models, task):
        if not search_space and models == ['all']:
            if task == 'classification':
                models_enum = ['xgb', 'catboost', 'adaboost','lgbm', 'logistic_regression', 'decision_tree']
                self.search_space = []
                for model in models_enum:
                    self.search_space.append(SearchSpaces.get_enum(model, task)[0])
            elif task == 'regression':
                models_enum = ['xgb', 'catboost', 'adaboost','lgbm', 'svr', 'decision_tree']
                for model in models_enum:
                    self.search_space.append(SearchSpaces.get_enum(model, task)[0])
            else:
                raise BaseException("This task in not implemented yet")
        elif not search_space and models != ['all']:
            self.__set_search_space_single_models__(models, task)
        elif search_space and models != ['all']:
            self.__retrieve_search_space_single_model__(
                models, self.search_space, self.task)
        elif search_space and models == ['all']:
            pass

    def __retrieve_search_space_single_model__(self, models, search_space, task):
        model_space = []
        for model in models:
            if model in ['xgb', 'catboost', 'adaboost', 'lgbm', 'logistic_regressor', 'svr', 'decision_tree']:
                for item in search_space:
                    if task == 'classification':
                        if item['estimator'][0] == model:
                            model_space.append(item)
                    elif task == 'regression':
                        if item['estimator'][0] == model:
                            model_space.append(item)
            else:
                raise BaseException("This model is not in the AutoML yet")
        if not model_space:
            for model in models:
                item = SearchSpaces.get_enum(model, task)[0]
                model_space.append(item)
        self.search_space = model_space

    def __set_search_space_single_models__(self, models, task):
        model_space = []
        for model in models:
            if model in ['xgb', 'catboost', 'adaboost', 'lgbm', 'logistic_regressor', 'svr', 'decision_tree']:
                model_space.append(SearchSpaces.get_enum(model, task)[0])
            else:
                print("Model ", model, " is not in the AutoML yet")
        if not model_space:
            raise BaseException("None of the given models were added to this tool."+ 
            "The options are: 'xgb', 'catboost', 'adaboost', 'lgbm', 'logistic_regressor', 'svr', 'decision_tree'")
        self.search_space = model_space



    def fit(self, X, y):
        if type(X) == np.ndarray:
            X = pd.DataFrame(X)
        if type(y) == np.ndarray:
            y = pd.Series(y)
            
        if self.task == 'classification':
            return self.run_grid_search_classification(X, y)
        elif self.task == 'regression':
            return self.run_grid_search_regression(X, y)
        else:
            raise BaseException("This task was not implemented yet")


    
    def run_grid_search_classification(self, X, y):
        ''' Runs a pipe with all the giveng settings'''

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y)

        param_grid = list(ParameterGrid(self.search_space))
        param_grid_selector = list(ParameterGrid(
        self.feature_selector_search_space))
        param_grid_selector_cp = copy.deepcopy(param_grid_selector)
        parameter_grid_cp = copy.deepcopy(param_grid)


        models = self.__run_pipe__(
            X_train, y_train, parameter_grid_cp, param_grid_selector_cp)
        best_model = self.__get_best_model__(self.task, models, X_test, y_test)

        best_model = best_model.fit(X, y)
        return best_model

    def run_grid_search_regression(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2)

        param_grid = list(ParameterGrid(self.search_space))

        param_grid_selector = list(ParameterGrid(
            self.feature_selector_search_space))

        param_grid_selector_cp = copy.deepcopy(param_grid_selector)

        models = self.__run_pipe__(
            X_train, y_train, param_grid, param_grid_selector_cp)
        best_model = self.__get_best_model__(
            self.task, models, X_test, y_test)

        best_model = best_model.fit(X, y)
        return best_model

    def __run_pipe__(self, X_train, y_train, model_space_params, feature_selector_space_params):
        '''
            Runs the complete pipe for every setting informed and returns the list of fitted models
        '''
        models = []
        if self.feature_selection:
            models = self.run_pipe_with_fs(model_space_params,feature_selector_space_params, X_train, y_train )  
        else:    
            models = self.run_pipe_with_model_params(model_space_params, X_train, y_train)
        return models


    def run_pipe_with_model_params(self, model_params, X_train, y_train):
        '''Creates, Run, and stores a full pipe for each possible parameter setting'''
        models = []
        for i, item in enumerate(model_params):  
            print("Fit ", i+1, "/ " + str(len(model_params)))
            params = copy.deepcopy(item)
            if self.task == 'classification':
                if item['estimator'] == 'decision_tree':
                    params.pop('estimator')
                    pipe = Pipeline(steps=[('imputer',  Base.CustomImputer()),
                                    ('dummie', Base.GetDummiesTransformer()),
                                    ('estimator', Base.Estimator(DecisionTreeClassifier(**params)))])

                elif item['estimator'] == 'xgb':
                    params.pop('estimator')
                    pipe = Pipeline(steps=[('imputer',  Base.CustomImputer()),
                                            ('dummie', Base.GetDummiesTransformer()),
                                            ('estimator', Base.Estimator(XGBClassifier(**params)))])

                elif item['estimator'] == 'catboost':
                    params.pop('estimator')
                    pipe = Pipeline(steps=[('imputer',Base.CustomImputer()),
                                            ('estimator', Base.Estimator(CatBoostClassifierScikit(params)))])

                elif item['estimator'] == 'adaboost':
                    params.pop('estimator')                         
                    pipe = Pipeline(steps=[('imputer',  Base.CustomImputer()),
                                            ('dummie', Base.GetDummiesTransformer()),
                                            ('estimator', Base.Estimator(AdaBoostClassifier(**params)))])

                elif item['estimator'] == 'lgbm':
                    params.pop('estimator')
                    pipe = Pipeline(steps=[('imputer',  Base.CustomImputer()),
                                            ('dummie', Base.GetDummiesTransformer()),
                                            ('estimator', Base.Estimator(LGBMClassifier(**params)))])
                elif item['estimator'] == 'logistic_regressor':
                    params.pop('estimator')
                    pipe = Pipeline(steps=[('imputer',Base.CustomImputer() ),
                                        ('dummie', Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(LogisticRegression(**params)))])
                else:
                    raise BaseException(
                        "This model in not implemented yet")
            elif self.task == 'regression':
                if item['estimator'] == 'xgb':
                    params.pop('estimator')
                    pipe = Pipeline(steps=[('imputer', Base.CustomImputer()),
                                        ('dummie', Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(XGBRegressor(**params)))])

                elif item['estimator'] == 'decision_tree':
                    params.pop('estimator')
                    pipe = Pipeline(steps=[('imputer', Base.CustomImputer()),
                                        ('dummie', Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(DecisionTreeRegressor(**params)))])

                elif item['estimator'] == 'catboost':
                    params.pop('estimator')
                    pipe = Pipeline(steps=[('imputer',  Base.CustomImputer()),
                                        ('estimator', Base.Estimator(CatBoostRegressorScikit(params)))])

                elif item['estimator'] == 'adaboost':
                    params.pop('estimator')
                    pipe = Pipeline(steps=[('imputer',  Base.CustomImputer()),
                                            ('dummie', Base.GetDummiesTransformer()),
                                            ('estimator', Base.Estimator(AdaBoostRegressor(**params)))])

                elif item['estimator'] == 'lgbm':
                    params.pop('estimator')
                    pipe = Pipeline(steps=[('imputer',  Base.CustomImputer()),
                                            ('dummie', Base.GetDummiesTransformer()),
                                            ('estimator', Base.Estimator(LGBMRegressor(**params)))])

                elif item['estimator'] == 'svr':
                    params.pop('estimator')                     
                    pipe = Pipeline(steps=[('imputer',  Base.CustomImputer()),
                                        ('dummie', Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(SVR(**params)))])
                else:
                    raise BaseException(
                        "This model in not implemented yet")
            models.append(pipe.fit(X_train, y_train))
        return models

    def run_pipe_with_fs(self, model_params, fs_params, X_train, y_train):
        '''Creates, Run, and stores a full pipe with feauture selection for each possible parameter setting'''
        models = []
        for i, fs_settings in enumerate(fs_params):
            for j, item in enumerate(model_params):
                print("Fit ", (i+1)*(j+1), "/ " + str(len(model_params)*len(fs_params)))
                params = copy.deepcopy(item)
                if self.task == 'classification':
                    if item['estimator'] == 'decision_tree':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer', Base.CustomImputer()),
                                                ('dummie', Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(DecisionTreeClassifier(**params)))])
                    elif item['estimator'] == 'xgb':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer', Base.CustomImputer()),
                                                ('dummie', Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(XGBClassifier(**params)))])
                    elif item['estimator'] == 'catboost':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer',Base.CustomImputer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(CatBoostClassifierScikit(params)))])
                    elif item['estimator'] == 'adaboost':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer',Base.CustomImputer()),
                                                ('dummie', Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(AdaBoostClassifier(**params)))])
                    elif item['estimator'] == 'lgbm':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer',Base.CustomImputer()),
                                                ('dummie', Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector( fs_settings)),
                                                ('estimator', Base.Estimator(LGBMClassifier(**params)))])
                    elif item['estimator'] == 'logistic_regressor':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer',Base.CustomImputer()),
                                                ('dummie', Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(LogisticRegression(**params)))])
                    else:
                        raise BaseException(
                            "This model in not implemented yet")
                elif self.task == 'regression':
                    if item['estimator'] == 'xgb':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer', Base.CustomImputer()),
                                                ('dummie', Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(XGBRegressor(**params)))])
                    elif item['estimator'] == 'decision_tree':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer', Base.CustomImputer()),
                                                ('dummie', Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(DecisionTreeRegressor(**params)))])
                    elif item['estimator'] == 'catboost':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer', Base.CustomImputer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(CatBoostRegressorScikit(params)))])
                    elif item['estimator'] == 'adaboost':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer',Base.CustomImputer()),
                                                ('dummie', Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector( fs_settings)),
                                                ('estimator', Base.Estimator(AdaBoostRegressor(**params)))])
                    elif item['estimator'] == 'lgbm':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer', Base.CustomImputer()),
                                                ('dummie', Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(LGBMRegressor(**params)))])
                    elif item['estimator'] == 'svr':
                        params.pop('estimator')
                        pipe = Pipeline(steps=[('imputer', Base.CustomImputer()),
                                                ('dummie', Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector( fs_settings)),
                                                   ('estimator', Base.Estimator(SVR(**params)))])
                    else:
                        raise BaseException(
                            "This model in not implemented yet")
                pipe.fit(X_train, y_train)
                models.append(pipe)
        return models
    def __get_best_model__(self, task, models, X_test, y_test):
        '''
            Finds the best model among the models returned by grid search"
        '''
        best_result_classification = 0
        y_pred = models[0].predict(X_test)
        best_result_regresion = Metrics.__theil_stat__(y_test, y_pred)
        if task == 'classification':
            best_model = {'model': models[0],
                          'auc': best_result_classification}
        elif task == 'regression':
            best_model = {'model': models[0],
                          'theil_stat': best_result_regresion}

        for model in models:
            y_pred = model.predict(X_test)
            if task == 'classification':
                if not self.compute_ks:
                    value = roc_auc_score(y_test, y_pred)
                    if value > best_result_classification:
                        best_model = {'model': model, 'auc': value}
                        best_result_classification = value
                else:
                    return self.get_best_model_by_ks(models, X_test, y_test)
            elif task == 'regression':
                value = Metrics.__theil_stat__(y_test, y_pred)
                if value < best_result_regresion:
                    best_model = {'model': model, 'theil_stat': value}
                    best_result_regresion = value
            print('Best score ', best_model[list(best_model.keys())[1]])
        return best_model['model']

    def get_best_model_by_ks(self, models, X, y):

        num_models_accepted = int(np.ceil(self.acceptance_rate*len(models)))
        best_models = ['']*(num_models_accepted)

        aucs = []

        for model in models:
            y_pred = model.predict(X)
            auc = roc_auc_score(y, y_pred)
            aucs.append((auc, model))

        aucs.sort(key=lambda x: x[0], reverse=True)
        best_models = aucs[:num_models_accepted]

        model_ks = []
        for item in best_models:
            y_pred = item[1].predict(X)
            ks = Metrics.__compute_ks_score__(y, y_pred)
            model_ks.append((ks, item[1]))

        model_ks.sort(key=lambda x: x[0], reverse=True)
        print('The model KS is: ', model_ks[0][0])
        return model_ks[0][1]
