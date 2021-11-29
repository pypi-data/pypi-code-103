
import numpy as np
from matplotlib import pyplot as plt

import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, KFold, ParameterGrid

from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_validate
from sklearn.ensemble import RandomForestRegressor, AdaBoostClassifier, AdaBoostRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVR

from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor

from sklearn.datasets import make_blobs, make_classification, make_regression

import optuna

from paml.metrics import Metrics
from paml.searches import Base
from paml.searches.optuna_objectives import OptunaObjectives
from paml.searches.Base import CustomImputer
from paml.searches.wrapper_catboost import CatBoostClassifierScikit, CatBoostRegressorScikit

class OptunaSearch:
    '''OptunaSearch implements fit, predict (from the estimator) get_best_model, get_best_model_by_ks (for classification only)'''
    def __init__(self, task:str, models:str = ['all'], n_trials:int = 10, n_folds:int = 5,
    compute_ks:bool = False,
    feature_selection:bool = False):
        self.models = models
        self.n_trials = n_trials
        self.task = task
        self.compute_ks = compute_ks
        self.n_folds = n_folds
        self.feature_selection = feature_selection
        

        self.feature_selector_search_space = [{'max_depth': [5]}]
        
        if self.models == ['all']:
            if self.task == 'classification':
                self.objectives = {'xgb' : OptunaObjectives.__objective_xgb_clf__,
                                    'catboost' : OptunaObjectives.__objective_catboost_classifier__,
                                    'lgbm': OptunaObjectives.__objective_lgbm_classifier__,
                                    'decision_tree': OptunaObjectives.__objective_decision_tree_classifier__,
                                    'adaboost': OptunaObjectives.__objective_adaboost_classifier__,
                                    'logistic_regression': OptunaObjectives.__objective__logistic_regression__}
            elif self.task == 'regression':
                self.objectives = {'xgb':OptunaObjectives.__objective_xgb_regressor__, 
                                   'catboost':OptunaObjectives.__objective_catboost_regressor__,
                                   'lgbm': OptunaObjectives.__objective_lgbm_regressor__,
                                   'decision_tree': OptunaObjectives.__objective_decision_tree_regressor__,
                                   'adaboost': OptunaObjectives.__objective_adaboost_regressor__,
                                   'svr': OptunaObjectives.__objective_svr_regressor__}
            else:
                raise BaseException('Task type not implemented yet')
        else:
            self.__set_model_objective_function__()
            
        if self.compute_ks and self.task == 'regression':
            raise BaseException("You can't compute KS for regression tasks, please set compute_ks to False")
    
    def __set_model_objective_function__(self):
        self.objectives = {}
        for model in self.models:
            if model == 'xgb':
                if self.task == 'classification':
                    self.objectives['xgb'] = OptunaObjectives.__objective_xgb_clf__
                elif self.task == 'regression':
                    self.objectives['xgb'] =  OptunaObjectives.__objective_xgb_regressor__
            elif model == 'catboost':
                if self.task == 'classification':
                    self.objectives['catboost'] = OptunaObjectives.__objective_catboost_classifier__
                elif self.task == 'regression':
                    self.objectives['catboost'] = OptunaObjectives.__objective_catboost_regressor__        
            elif model == 'lgbm':
                if self.task == 'classification':
                    self.objectives['lgbm'] = OptunaObjectives.__objective_lgbm_classifier__
                elif self.task == 'regression':
                    self.objectives['lgbm'] =  OptunaObjectives.__objective_lgbm_regressor__
            elif model == 'decision_tree':
                if self.task == 'classification':
                    self.objectives['decision_tree'] = OptunaObjectives.__objective_decision_tree_classifier__
                elif self.task == 'regression':
                    self.objectives['decision_tree'] = OptunaObjectives.__objective_decision_tree_regressor__
            elif model == 'adaboost':
                if self.task == 'classification':
                    self.objectives['adaboost'] = OptunaObjectives.__objective_adaboost_classifier__
                elif self.task == 'regression':
                    self.objectives['adaboost'] = OptunaObjectives.__objective_adaboost_regressor__
            elif model == 'svr':
                self.objectives['svr'] = OptunaObjectives.__objective_svr_regressor__
            elif model == 'logistic_regression':
                self.objectives ['logistic_regression'] = OptunaObjectives.__objective__logistic_regression__
            else:
                raise BaseException('This model was not added to the tool yet')
                
    def __tune_params__(self, X, y, objective, direction, n_trials):
        objective_lambda = lambda trial: objective(trial, X, y)
        study = optuna.create_study(study_name = 'OptunaStudy', direction = direction)
        study.optimize(objective_lambda, n_trials = n_trials, n_jobs=-1)
        return study.best_params
    

    def __get_internal_best_model__(self, models_per_objective):
        best_metric = models_per_objective[0][0]
        best_model = models_per_objective[0][1]
        if self.task == 'classification':
            for item in models_per_objective:
                if item[0] > best_metric:
                    best_metric = item[0]
                    best_model = item[1]
        elif self.task == 'regression':
            for item in models_per_objective:
                if item[0] < best_metric:
                    best_metric = item[0]
                    best_model = item[1]
        return best_model
    
    def __get_best_model_by_simple_metric__(self, results):
        best_metric = results[0][0]
        best_model = results[0][1]
        if self.task == 'classification':
            for item in results:
                if item[0] > best_metric:
                    best_metric = item[0]
                    best_model = item[1]
        elif self.task == 'regression':
            for item in results:
                if item[0] < best_metric:
                    best_metric = item[0]
                    best_model = item[1]
        
        print("Best score: ", best_metric)
        return best_model
            
        
    def __get_best_model_by_ks__(self, ks_results):
        best_model = ks_results[0][1]
        best_ks = ks_results[0][0]
        for item in ks_results:
            if item[0] > best_ks:
                best_ks = item[0]
                best_model = item[1]
        print("KS: ", best_ks)
        return best_model
        
    def __fit_models__(self, objectives, X, y, task):
        models = []
        if type(X) == np.ndarray:
            X = pd.DataFrame(X)
        if type(y) == np.ndarray:
            y = pd.Series(y)
        best_models = []
        
       
        imputer = CustomImputer()
        X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

        self.feature_selector_settings = list(ParameterGrid(self.feature_selector_search_space))
        
        if task == 'classification':
            kfold =  StratifiedKFold(n_splits = self.n_folds)  
            for model_name, obj_function in objectives.items():
                pred = []
                pipe = None
                models_per_objective = []
                for train_idx, test_idx in kfold.split(X, y):
                    params = self.__tune_params__(X.iloc[train_idx,:], y.iloc[train_idx], obj_function, "maximize", self.n_trials)
                    if self.feature_selection:
                        pipe = self.get_pipe_with_feature_selection(model_name, self.task, params)
                    else:
                        pipe = self.get_pipe(model_name, self.task, params)

                    pipe.fit(X.iloc[train_idx,:], y.iloc[train_idx])
                    pred = pipe.predict(X.iloc[test_idx,:])

                    metric = roc_auc_score(y.iloc[test_idx], pred)
                    models_per_objective.append((metric, pipe))     
                best_models.append(self.__get_internal_best_model__(models_per_objective))
                
        elif task == 'regression':
            kfold =  KFold(n_splits = self.n_folds)
            for model_name, obj_function in objectives.items():
                print(model_name)
                pred = []
                pipe = None
                models_per_objective = []
                for train_idx, test_idx in kfold.split(X, y):
                    params = self.__tune_params__(X.iloc[train_idx,:], y.iloc[train_idx], obj_function, "minimize", self.n_trials)
                    if self.feature_selection:
                        pipe = self.get_pipe_with_feature_selection(model_name, self.task, params)
                    else:
                        pipe = self.get_pipe(model_name, task, params)
                    pipe.fit(X.iloc[train_idx,:], y.iloc[train_idx])
                    pred = pipe.predict(X.iloc[test_idx,:])
                    
                    metric = Metrics.__theil_stat__(y.iloc[test_idx], pred)
                    models_per_objective.append((metric, pipe))
                best_models.append(self.__get_internal_best_model__(models_per_objective))
        return best_models
    
    def get_pipe_with_feature_selection(self, model_name, task, params):
        for fs_settings in self.feature_selector_settings:
            if task == 'classification':
                if model_name == 'xgb':
                        pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                                ("dummies", Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(XGBClassifier(**params)))])
                elif model_name == 'catboost':
                    pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                            ("dummies", Base.GetDummiesTransformer()),
                                            ('fs', Base.FeatureSelector(fs_settings)),
                                            ('estimator', Base.Estimator(CatBoostClassifierScikit(params)))])                   
                elif model_name == 'lgbm':
                    pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                            ("dummies", Base.GetDummiesTransformer()),
                                            ('fs', Base.FeatureSelector(fs_settings)),
                                            ('estimator', Base.Estimator(LGBMClassifier(**params)))]) 
                elif model_name == 'decision_tree':
                    pipe = Pipeline(steps = [('imputer',CustomImputer()),
                                            ("dummies", Base.GetDummiesTransformer()),
                                            ('fs', Base.FeatureSelector(fs_settings)),
                                            ('estimator', Base.Estimator(DecisionTreeClassifier(**params)))]) 
                elif model_name == 'adaboost':
                    pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                            ("dummies", Base.GetDummiesTransformer()),
                                            ('fs', Base.FeatureSelector(fs_settings)),
                                            ('estimator', Base.Estimator(AdaBoostClassifier(**params)))])
                elif model_name == 'logistic_regression':       
                    pipe = Pipeline(steps = [('imputer',CustomImputer()),
                            ('fs', Base.FeatureSelector(fs_settings)),
                            ('estimator', Base.Estimator(LogisticRegression(**params)))])    
                else:
                    raise BaseException("Model not added to the tool yet")

            elif task == 'regression':
                if model_name == 'xgb':
                        pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                                ("dummies", Base.GetDummiesTransformer()),
                                                ('fs', Base.FeatureSelector(fs_settings)),
                                                ('estimator', Base.Estimator(XGBRegressor(**params)))])
                elif model_name == 'catboost':
                    pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                            ('fs', Base.FeatureSelector(fs_settings)),
                                            ('estimator', Base.Estimator(CatBoostRegressorScikit(params)))])                   
                elif model_name == 'lgbm':
                    pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                            ('fs', Base.FeatureSelector(fs_settings)),
                                            ('estimator', Base.Estimator(LGBMRegressor(**params)))]) 
                elif model_name == 'decision_tree':
                    pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                            ("dummies", Base.GetDummiesTransformer()),
                                            ('fs', Base.FeatureSelector(fs_settings)),
                                            ('estimator', Base.Estimator(DecisionTreeRegressor(**params)))]) 
                elif model_name == 'adaboost':
                    pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                            ("dummies", Base.GetDummiesTransformer()),
                                            ('fs', Base.FeatureSelector(fs_settings)),
                                            ('estimator', Base.Estimator(AdaBoostRegressor(**params)))])
                elif model_name == 'svr':       
                    pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                            ('fs', Base.FeatureSelector(fs_settings)),
                                            ('estimator', Base.Estimator(SVR(**params)))])    
                else:
                    raise BaseException("Model not added to the tool yet")
        return pipe

    def get_pipe(self, model_name, task, params):
        if task == 'classification':
            if model_name == 'xgb':
                    pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                            ("dummies", Base.GetDummiesTransformer()),
                                            ('estimator', Base.Estimator(XGBClassifier(**params)))])
            elif model_name == 'catboost':
                pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                        ("dummies", Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(CatBoostClassifierScikit(params)))])                   
            elif model_name == 'lgbm':
                pipe = Pipeline(steps = [('imputer',CustomImputer()),
                                        ("dummies", Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(LGBMClassifier(**params)))]) 
            elif model_name == 'decision_tree':
                pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                        ("dummies", Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(DecisionTreeClassifier(**params)))]) 
            elif model_name == 'adaboost':
                pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                        ("dummies", Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(AdaBoostClassifier(**params)))])
            elif model_name == 'logistic_regression':       
                pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                        ("dummies", Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(LogisticRegression(**params)))])    
            else:
                raise BaseException("Model not added to the tool yet")
        elif task == 'regression':
            if model_name == 'xgb':
                    pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                            ("dummies", Base.GetDummiesTransformer()),
                                            ('estimator', Base.Estimator(XGBRegressor(**params)))])
            elif model_name == 'catboost':
                pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                        ("dummies", Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(CatBoostRegressorScikit(params)))])                   
            elif model_name == 'lgbm':
                pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                        ("dummies", Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(LGBMRegressor(**params)))]) 
            elif model_name == 'decision_tree':
                pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                        ("dummies", Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(DecisionTreeRegressor(**params)))]) 
            elif model_name == 'adaboost':
                pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                        ("dummies", Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(AdaBoostRegressor(**params)))])
            elif model_name == 'svr':       
                pipe = Pipeline(steps = [('imputer', CustomImputer()),
                                        ("dummies", Base.GetDummiesTransformer()),
                                        ('estimator', Base.Estimator(SVR(**params)))])    
            else:
                raise BaseException("Model not added to the tool yet")
        return pipe
      
    def __get_best_model__(self, X, y, task, ks_flag, models):
        if ks_flag and task == 'classification':
            ks_results = []
            for model in models:
                model.fit(X, y)
                y_pred = model.predict(X)
                ks = Metrics.__compute_ks_score__(y, y_pred)
                ks_results.append((ks, model))  
            return self.__get_best_model_by_ks__(ks_results)

        if not ks_flag and task == 'classification':
            roc_results = []
            for model in models:
                model.fit(X, y)
                y_pred = model.predict(X)
                roc = roc_auc_score(y, y_pred)
                roc_results.append((roc, model))
            return self.__get_best_model_by_simple_metric__(roc_results)     
        elif task == 'regression':
            results = []
            for model in models:
                model.fit(X, y)
                y_pred = model.predict(X)
                theil_stat = Metrics.__theil_stat__(y, y_pred)
                results.append((theil_stat, model))
            return self.__get_best_model_by_simple_metric__(results)
        else:
            raise BaseException("Task not implemented yet")
   
    def fit(self, X, y):           
        models = self.__fit_models__(self.objectives, X, y, self.task)
        return self.__get_best_model__(X, y, self.task, self.compute_ks, models)