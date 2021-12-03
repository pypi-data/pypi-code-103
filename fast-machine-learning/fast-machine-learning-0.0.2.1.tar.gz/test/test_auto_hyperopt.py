
import sys, numpy as np
sys.path.append("..")
from fml.configs.auto_config import AutoConfig
from fml.validates.validate_compat import validate_switch
from hyperopt import Trials, tpe, STATUS_OK, fmin
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
X, Y = load_boston(return_X_y=True)
# X = X[:100, :]
# Y = Y[:100]

trials = Trials()
# space = AutoConfig().regression
space = AutoConfig().split_data
trials_ = []
performances = []

# def f(params):

#     print(params)
#     algo = params["algo"]
#     kwargs = params["kwargs"]

#     loo = validate_switch(5, algo, X, Y, **kwargs)
#     error = loo["rmse"]
#     print(f"{error}, {loo['r2_score']}")
#     performances.append([error, loo['r2_score']])
#     trials_.append(params)
#     return {'loss': error, 'status': STATUS_OK}

def f(params):
    
    # print(params)
    xtrain, xtest, ytrain, ytest = train_test_split(X, Y, test_size=params["test_size"], random_state=params["random_state"])
    loo = validate_switch(5, params["algorithms"], xtrain, ytrain)
    test = validate_switch("test", params["algorithms"], xtrain, ytrain, xtest, ytest)
    loo_error = loo["rmse"]
    test_error = test["rmse"]
    if loo_error > test_error:
        error = loo_error + test_error
    else:
        error = loo_error
    performances.append([error, loo['r2_score'], test["r2_score"]])
    trials_.append(params)
    return {'loss': error, 'status': STATUS_OK}


best = fmin(fn=f, space=space, algo=tpe.suggest, max_evals=100, trials=trials, verbose=True, trials_save_file="1.txt")
print(best)

performances = np.array(performances)
best_ = performances[performances[:, 0]==performances[:, 0].min()]
best_i = np.argmin(performances[:, 0])
best_params = trials_[best_i]

xtrain, xtest, ytrain, ytest = train_test_split(X, Y, test_size=best_params["test_size"],random_state=best_params["random_state"])
loo = validate_switch(5, best_params["algorithms"], xtrain, ytrain)
test = validate_switch("test", best_params["algorithms"], xtrain, ytrain, xtest, ytest)
