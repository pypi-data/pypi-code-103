import numpy as np
import pandas as pd
import logging


from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.model_selection import GridSearchCV as GridCV
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVR

from sklearn.metrics import roc_auc_score


from xgboost import XGBClassifier, XGBRegressor
from lightgbm import  LGBMClassifier, LGBMRegressor

from boruta import BorutaPy

from paml.searches import SearchSpaces
from paml.metrics import Metrics
from paml.searches.Base import CustomImputer, FeatureSelector, GetDummiesTransformer
from paml.searches.wrapper_catboost import CatBoostClassifierScikit, CatBoostRegressorScikit


class GridSearchCV:
    '''GridSearch implements fit, predict, get_best_model by KS (for classification only) '''
    def __init__(self, n_folds : int = 5,  verbose: int = 10, n_jobs: int = -1, 
                search_space: dict = None,  models:list=['all'], fs_params = {'max_depth': 5},
                task:str='classification', compute_ks: bool = False, acceptance_rate:float = 0.01,
                feature_selection:bool = False):

        self.search_space = search_space
        self.verbose = verbose
        self.n_jobs = n_jobs
        self.n_folds = n_folds
        self.models = models
        self.task = task
        self.compute_ks = compute_ks
        self.acceptance_rate = acceptance_rate
        self.feature_selection = feature_selection
        self.fs_params = fs_params     
       
        self.__set_model_params_grid__(search_space = self.search_space, models =  self.models, task = self.task)
                                                  
    def __retrieve_search_space_single_model__(self, models, search_space, task):    
            model_space = []
            for model in models:
                if model in ['xgb', 'catboost', 'adaboost', 'lgbm', 'logistic_regressor', 'svr', 'decision_tree']:
                    for item in search_space:
                        if task == 'classification':
                            if item['clf'][0] == model:
                                item['clf'] = [self.get_estimator_instance_classifier(model)]
                                model_space.append(item)
                        elif task == 'regression':
                            if item['rgs'][0] == model:
                                item['rgs'] = [self.get_estimator_instance_regressor(model)]
                                model_space.append(item)
                        else: 
                            raise BaseException("This task is not implemented yet")
                else:
                    raise BaseException("This model is not in the AutoML yet")

                if not model_space:
                    for model in models:
                        search_item  = SearchSpaces.get_enum(model, task)
                        search_item = self.treat_search_space_keys(search_item)
                        search_item = self.set_estimator_instance(search_item)
                        if self.feature_selection:
                            search_item[0]['fs__params'] = [self.fs_params]
                        model_space.append(search_item[0])
                self.search_space = model_space

    def __set_model_params_grid__(self, search_space, models, task):
            if not search_space and models == ['all']:
                if task == 'classification':
                    models_enum = ['xgb', 'catboost', 'adaboost','lgbm', 'logistic_regression', 'decision_tree']
                    self.search_space = []
                    for model in models_enum:
                        search_item = SearchSpaces.get_enum(model, task)
                        search_item = self.treat_search_space_keys(search_item)
                        search_item = self.set_estimator_instance(search_item)
                        if self.feature_selection:
                            search_item[0]['fs__params'] = [self.fs_params]
                        self.search_space.append(search_item[0])
                elif task == 'regression':
                    models_enum = ['xgb', 'catboost', 'adaboost','lgbm', 'svr', 'decision_tree']
                    self.search_space = []
                    for model in models_enum:
                        search_item = SearchSpaces.get_enum(model, task)
                        search_item = self.treat_search_space_keys(search_item)
                        search_item = self.set_estimator_instance(search_item)
                        if self.feature_selection:
                            search_item[0]['fs__params'] = [self.fs_params]
                        self.search_space.append(search_item[0])                                      
                else:
                    raise BaseException("This task is not implemented yet")
            elif not search_space and models != ['all']:
                self.__set_search_space_single_models__(models, task)
            elif search_space and models != ['all']:
                self.search_space = self.treat_search_space_keys(search_space) 
                self.__retrieve_search_space_single_model__(models, self.search_space, self.task)
            else:
                pass

    def __set_search_space_single_models__(self, models, task):
        model_space = []
        for model in models:
            if model in ['xgb', 'catboost', 'adaboost', 'lgbm', 'logistic_regressor', 'svr', 'decision_tree']:
                search_item = (SearchSpaces.get_enum(model, task))
                search_item = self.treat_search_space_keys(search_item)
                search_item = self.set_estimator_instance(search_item)
                if self.feature_selection:
                    search_item[0]['fs__params'] = [self.fs_params]
                model_space.append(search_item[0])         
            else:
                print("Model ", model, " is not in the AutoML yet")
        if not model_space:
            raise BaseException("None of the given models were added to this tool."+ 
            "The options are: 'xgb', 'catboost', 'adaboost', 'lgbm', 'logistic_regressor', 'svr', 'decision_tree'")
        self.search_space = model_space

    def create_grid_classification(self):
        '''
            Creates a grid search according to constructor specs
        '''
        estimator_ = self.get_estimator_instance_classifier(self.models[0])
        

        if self.feature_selection:
            pipe = Pipeline(steps = [
                                    ('imputer', CustomImputer()),
                                    ('get_dummies', GetDummiesTransformer()),
                                    ('fs', FeatureSelector(self.fs_params)),
                                    ('clf', estimator_)])
        else:
            pipe = Pipeline(steps = [ ('imputer', CustomImputer()),
                                      ('get_dummies', GetDummiesTransformer()),
                                    ('clf', estimator_)])
                 
        cv = StratifiedKFold(n_splits = self.n_folds, shuffle=True, random_state=42)
        scoring = {"AUC": "roc_auc"}


        if not self.verbose:
             self.verbose = 10

        grid = GridCV(estimator= pipe,
                          param_grid = self.search_space,
                          cv = cv,
                          scoring = scoring,
                          return_train_score= True,
                          refit = "AUC",
                          verbose = self.verbose,
                          n_jobs =self.n_jobs)
        return grid

    def create_grid(self):
        if self.task == 'classification':
            return self.create_grid_classification()
        elif self.task == 'regression':
            return self.create_grid_regression()
        else:
            raise BaseException("Task not implemented yet")

    def set_estimator_instance(self, search_space):
        new_space = []
        for i, item in enumerate(search_space):
            new_space.append(item)
            if self.task == 'classification':
                new_space[i]['clf'] = [self.get_estimator_instance_classifier(new_space[i]['clf'][0])] 
            elif self.task == 'regression':
                new_space[i]['rgs'] = [self.get_estimator_instance_regressor(new_space[i]['rgs'][0])]
        return new_space  

    def get_estimator_instance_classifier(self, model):
        estimator = {}
        if  model == 'xgb':
            estimator = XGBClassifier(use_label_encoder=False)
        elif model == 'catboost' or model ==  'all':
            estimator = CatBoostClassifierScikit()
        elif model == 'adaboost':
            estimator = AdaBoostClassifier()
        elif model == 'lgbm':
            estimator = LGBMClassifier()
        elif model == 'decision_tree':
            estimator = DecisionTreeClassifier()
        elif model == 'logistic_regressor':
            estimator = LogisticRegression()
        return estimator


    def get_estimator_instance_regressor(self, model):
        estimator = {}
        if model == 'xgb':
            estimator = XGBRegressor(label_encoder = False)
        elif model == 'catboost' or model == 'all':
            estimator = CatBoostRegressorScikit()
        elif model == 'adaboost':
            estimator = AdaBoostRegressor()
        elif model == 'lgbm':
            estimator = LGBMRegressor()
        elif model == 'decision_tree':
            estimator = DecisionTreeRegressor()
        elif model == 'svr':
            estimator = SVR()
        return estimator

    def create_grid_regression(self):
        '''
            Creates a grid search for regression according to the specs
        '''        
        self.imputer =  CustomImputer()               
        estimator = self.get_estimator_instance_regressor(self.models[0])

        if self.feature_selection:
            pipe = Pipeline(steps = [('imputer', CustomImputer()),
                            ('get_dummies', GetDummiesTransformer()),
                            ('fs', FeatureSelector(self.fs_params)),
                            ('rgs', estimator) ])
        else:
            pipe = Pipeline(steps = [('imputer',  CustomImputer()),
                                    ('get_dummies', GetDummiesTransformer()),
                                     ('rgs', estimator) ])

        cv = KFold(n_splits = self.n_folds, shuffle=True, random_state=42)
        theil_score = Metrics.theil_stat()
        scoring = {"theil": theil_score}

        # mse = make_scorer(score_func= mean_squared_error, needs_proba= False, greater_is_better=False)
        # scoring = {"neg_root_mean_squared_error": mse}


        if not self.verbose:
             self.verbose = 10

        grid = GridCV(estimator= pipe,
                          param_grid = self.search_space,
                          cv = cv,
                          scoring = scoring,
                          return_train_score= True,
                          refit = "theil",
                          verbose = self.verbose,
                          n_jobs =self.n_jobs)
        return grid

    def fit_model(self, X, y):
        '''
            Run a given grid search and returns the best model
        '''
        if type(X) == np.ndarray:
            X = pd.DataFrame(X)
        if type(y) == np.ndarray:
            y = pd.Series(y)
        


        best_model = []
        my_grid = self.create_grid()
        best_model = my_grid.fit(X,y)
        
        if self.task == 'classification':
            if self.compute_ks:
                best_model = self.get_best_model_by_ks(best_model, X, y)
                return best_model
            else:
                return best_model
        else:
             return best_model

    def get_best_model_by_ks(self, grid, X, y):

        grid_results = pd.DataFrame(grid.cv_results_)
        grid_results.sort_values(by='rank_test_AUC', inplace = True)
        num_models_accepted = int(np.ceil(self.acceptance_rate*len(grid_results)))
        best_models = ['']*(num_models_accepted)

        aucs = []
        cv = StratifiedKFold(n_splits = self.n_folds, shuffle=True, random_state=42)
        scoring = {"AUC": "roc_auc"}
        for params in grid_results.params:
            params = self.set_params_values_as_list(params)
            scoring = {"AUC": "roc_auc"}

            if self.feature_selection:
                pipe = Pipeline(steps = [('imputer', CustomImputer()),
                            ('get_dummies', GetDummiesTransformer()),
                            ('fs', BorutaPy(estimator = self.fs_estimator)),
                            ('clf', params['clf'][0]) ])
            else:
                pipe = Pipeline(steps = [('imputer',CustomImputer() ),
                        ('get_dummies', GetDummiesTransformer()),
                        ('clf', params['clf'][0]) ])

            model = GridCV(estimator= pipe,
                          param_grid = params,
                          cv = cv,
                          scoring = scoring,
                          return_train_score= True,
                          refit = "AUC",
                          verbose = self.verbose,
                          n_jobs =self.n_jobs)
            model.fit(X,y)
            y_pred = model.predict(X)
            auc = roc_auc_score(y, y_pred)
            aucs.append((auc, model))

        aucs.sort(key=lambda x: x[0], reverse=True)
        best_models = aucs[:num_models_accepted]

        model_ks = []
        for item in best_models:
            y_pred =  item[1].predict(X)
            ks = Metrics.__compute_ks_score__(y, y_pred)
            model_ks.append((ks, item[1]))

        model_ks.sort(key=lambda x: x[0], reverse=True)
        print('The model KS is: ', model_ks[0][0])
        return model_ks[0][1]

    def set_params_values_as_list(self, params):
        new_params = {}
        for key,value in params.items():
            new_params[key] =[value]

        return new_params

    def parametrize_model(self, params, model):
        if isinstance(model, CatBoostClassifierScikit):
            return CatBoostClassifierScikit(params)
        elif isinstance(model,CatBoostRegressorScikit):
            return CatBoostRegressorScikit(params)
        elif isinstance(model, XGBClassifier):
            return XGBClassifier(**params)
        elif isinstance(model, XGBRegressor):
            return XGBRegressor(**params)
        elif isinstance(model, AdaBoostClassifier):
            return AdaBoostClassifier(**params)
        elif isinstance(model, AdaBoostRegressor):
            return AdaBoostRegressor(**params)
        elif isinstance(model, LGBMClassifier):
            return LGBMClassifier(**params)
        elif isinstance(model, LGBMRegressor):
            return LGBMRegressor(**params)
        elif isinstance(model, DecisionTreeClassifier):
            return DecisionTreeClassifier(**params)
        elif isinstance(model, DecisionTreeRegressor):
            return DecisionTreeRegressor(**params)
        elif isinstance(model, LogisticRegression):
            return LogisticRegression(**params)
        elif isinstance(model, SVR):
            return SVR(**params)
        else:
            raise BaseException ("Model not implemented yet")

    def treat_search_space_keys(self, search_space):
        new_space = []
        for i, item in enumerate(search_space):
            new_space.append({})
            for key, value in item.items():
                if key != 'estimator' and key != 'fs__params':
                    if self.task == 'classification':
                        new_space[i]['clf__'+key] = value
                    elif self.task == 'regression':
                        new_space[i]['rgs__'+key] = value
                else:
                    if key != 'fs__params':
                        if self.task == 'classification':
                            new_space[i]['clf'] = value
                        elif self.task == 'regression':
                            new_space[i]['rgs'] = value
        return new_space   