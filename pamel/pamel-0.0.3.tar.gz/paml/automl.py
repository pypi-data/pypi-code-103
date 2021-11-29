from paml.searches import OptunaSearch
from paml.searches import GridSearchCV
from paml.searches import GridSearch

class AutoML:
    ''''
    Parameters:
        task - Machine Learning task, it can be ‘regression’ or ‘classification’
        
        search_space: list Default None - The parameter search_space for one or more models.If not defined by 
        the user the  software will provide a default space.
        
        search: string Default: Optuna -  The search type to be performed by the autoML. The available options are ‘GridSearch’, ‘GridSearchCV’ and ‘OptunaSearch’. When using the ‘OptunaSearch’ is not possible to define a search_space

        models: list: Default: ['all'] - The model(s) that will be used in the autoML. It is mandatory to pass a list with the models, even if there is only one model. If option ['all'] is passed the tool will use all the models implemented. Available models are: DecisionTreeClassifier, DecisionTreeRegressor,  CatBoostClassifier, CatBoostRegressor, LGBMClasssifier, LGBMRegressor, XGBoostClassifier, XGBoostRgressor, AdaBoostClassifier, AdaBoostRegressor, LogisticRegression and SVR.  When passing one of these models use one of the following alias: decision_tree, catboost, lgbm, xgb, adaboost, logistic_regression, svr or all.

        compute_ks: bool: Default: False - Boolean flag for using the Kolmogorov-Smirnov (KS) score as measure for choosing between the best ranked AUC scored models. It is only used in classification tasks.

        n_folds: int: Default: 5 - Number of folds used in cross-validation. It is only used in GridSearchCV and OptunaSearch.

        feature_selection: bool: Deafult: False - Boolean flag for performing or not feature selection on the dataset.

        fs_params: dict: Default: {'max_depth': [5]} - Dict of parameterization of random forest estimator used in feature selection. Only used when feature_selection is True.

        acceptance_rate: float: Default 0.001 - percentage of number of models acceptation of all possible combinations trained by the searched. It is used when the flag compute_ks is set to True. From the 0.1% best ranked models, the model with best KS is chosen.

        n_trials : int Deafult: 10 - Number of trials for the Optuna search.

        n_jobs: int Default: - 1 Number of jobs to run in parallel. -1 means using all processors

    '''
    def __init__(self,  task: str, search_space=None, search: str = 'OptunaSearch', models=['all'],
                 compute_ks: bool = False, n_folds: int = 5, feature_selection=False, fs_params={'max_depth': [5]},
                 acceptance_rate: float = 0.01,
                 n_trials: int = 10,
                 n_jobs: int = -1):

        self.search = search
        self.task = task
        self.models = models
        self.compute_ks = compute_ks
        self.search_space = search_space
        self.n_folds = n_folds
        self.acceptance_rate = acceptance_rate
        self.n_trials = n_trials
        self.feature_selection = feature_selection
        self.n_jobs = n_jobs
        self.fs_params = fs_params

    def fit(self, X, y):

        if self.search == 'GridSearchCV':
            gridSearchCV = GridSearchCV(search_space=self.search_space, n_jobs=self.n_jobs,
                                        n_folds=self.n_folds, models=self.models, task=self.task,
                                        compute_ks=self.compute_ks, feature_selection=self.feature_selection,
                                        acceptance_rate=self.acceptance_rate, fs_params={'max_depth': 5})

            best_model = gridSearchCV.fit_model(X, y)
            return best_model
        elif self.search == 'GridSearch':
            gridSearch = GridSearch(search_space=self.search_space,
                                    models=self.models, task=self.task,
                                    compute_ks=self.compute_ks, acceptance_rate=self.acceptance_rate,
                                    feature_selection=self.feature_selection)
            model = gridSearch.fit(X, y)
            return model

        elif self.search == 'OptunaSearch':
            if self.search_space:
                print("You can't use a search space when using optuna")

            Optuna = OptunaSearch(n_trials=self.n_trials, task=self.task,
                                  compute_ks=self.compute_ks, n_folds=self.n_folds,
                                  models=self.models,
                                  feature_selection=self.feature_selection)
            best_model = Optuna.fit(X, y)
            return best_model
        else:
            raise BaseException("Search not implemented yet")
