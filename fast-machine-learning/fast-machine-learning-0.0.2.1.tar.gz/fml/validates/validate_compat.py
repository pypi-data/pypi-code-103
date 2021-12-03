
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, confusion_matrix, accuracy_score
from sklearn.model_selection import LeaveOneOut, KFold
import numpy as np

def validate_switch(loo_flag=False, model=None, X=None, Y=None, X_test=None, Y_test=None, **modelparams):
    
    if loo_flag == False:
        built_model = model(**modelparams).fit(X, Y)
        preds = built_model.predict(X)
        ytests = Y
    elif loo_flag == True or isinstance(loo_flag, int):
        if loo_flag == True:
            loo_or_kf = LeaveOneOut()
        elif isinstance(loo_flag, int):
            loo_or_kf = KFold(n_splits=loo_flag, shuffle=True)
        loo_or_kf.get_n_splits(X)
        preds = []
        ytests = []
        for itrain, itest in loo_or_kf.split(X):
            xtrain, xtest = X[itrain], X[itest]
            ytrain, ytest = Y[itrain], Y[itest]
            preds += model(**modelparams).fit(xtrain, ytrain).predict(xtest).tolist()
            ytests += ytest.tolist()
        preds = np.array(preds)
        ytests = np.array(ytests)
        built_model = model(**modelparams).fit(X, Y)
    elif X_test is not None:
        built_model = model(**modelparams).fit(X, Y)
        preds = built_model.predict(X_test)
        ytests = Y_test
    if len(set(Y.tolist())) <= 8:
        validate_results = dict(
            confusion_matrix = confusion_matrix(ytests, preds),
            accuracy_score = accuracy_score(ytests, preds),
            model = built_model,
            preds = preds,
            true_value = ytests
            )
    else:
        validate_results = dict(
            r2_score = r2_score(ytests, preds),
            mse = mean_squared_error(ytests, preds),
            mae = mean_absolute_error(ytests, preds),
            rmse = np.sqrt(mean_squared_error(ytests, preds)),
            model = built_model,
            preds = preds,
            true_value = ytests
            )   
    return validate_results



def validate(model=None, x_train=None, y_train=None, x_test=None, y_test=None, **modelparams):
    
    if x_test is not None:

        validate_results = dict(
            train = validate_switch(False, model, x_train, y_train, **modelparams),
            test = validate_switch("test", model, x_train, y_train, x_test, y_test, **modelparams),
            loo = validate_switch(True, model, x_train, y_train, **modelparams),
            cv10 = validate_switch(10, model, x_train, y_train, **modelparams),
            cv5 = validate_switch(5, model, x_train, y_train, **modelparams)
            )
    else:
        validate_results = dict(
            train = validate_switch(False, model, x_train, y_train, **modelparams),
            loo = validate_switch(True, model, x_train, y_train, **modelparams),
            cv10 = validate_switch(10, model, x_train, y_train, **modelparams),
            cv5 = validate_switch(5, model, x_train, y_train, **modelparams)
            )
    
    return validate_results

def validate_nocv(model=None, x_train=None, y_train=None, x_test=None, y_test=None, **modelparams):
    
    if x_test is not None:
    
        validate_results = dict(
            train = validate_switch(False, model, x_train, y_train, **modelparams),
            test = validate_switch("test", model, x_train, y_train, x_test, y_test, **modelparams),
            loo = validate_switch(True, model, x_train, y_train, **modelparams),
            )
    else:
        validate_results = dict(
            train = validate_switch(False, model, x_train, y_train, **modelparams),
            loo = validate_switch(True, model, x_train, y_train, **modelparams),
            )
    
    return validate_results


    
def validate_from_trees(model=None, max_features=None, x_train=None, y_train=None, x_test=None, y_test=None, cv=True, **modelparams):
    results = []
    if isinstance(max_features, int):
        max_features = [max_features]
    elif isinstance(max_features, list):
        max_features = [ int(i) for i in max_features]
    elif isinstance(max_features, float):
        max_features = [int(max_features)]
    for max_feature in max_features:
        selectfrommodel = SelectFromModel(
            model(**modelparams), 
            threshold=-np.inf, max_features=max_feature
            ).fit(x_train, y_train)
        feature_mask = selectfrommodel.get_support()
        if x_test is not None:
            if cv:
                result = validate(model, x_train[:, feature_mask], 
                                 y_train, x_test[:, feature_mask], 
                                 y_test, **modelparams)
            else:
                result = validate_nocv(model, x_train[:, feature_mask], 
                                 y_train, x_test[:, feature_mask], 
                                 y_test, **modelparams)
        else:
            if cv:
                result = validate(model, x_train[:, feature_mask], 
                                 y_train, **modelparams)
            else:
                result = validate_nocv(model, x_train[:, feature_mask], 
                             y_train, **modelparams)
        # results.append([max_feature]+ list(modelparams.values()) + [result["loo"]["r2_score"]] +[result])
        result.update(dict(feature_mask=feature_mask))
        results.append(result)
    return results


def validate_switch_from_trees(loo_flag=None, model=None, max_features=None, x_train=None, y_train=None, x_test=None, y_test=None, **modelparams):
    results = []
    if isinstance(max_features, int):
        max_features = [max_features]
    elif isinstance(max_features, list):
        max_features = [ int(i) for i in max_features]
    elif isinstance(max_features, float):
        max_features = [int(max_features)]
    for max_feature in max_features:
        selectfrommodel = SelectFromModel(
            model(**modelparams), 
            threshold=-np.inf, max_features=max_feature
            ).fit(x_train, y_train)
        feature_mask = selectfrommodel.get_support()
        if x_test is not None:
            result = validate_switch(loo_flag, model, x_train[:, feature_mask], 
                             y_train, x_test[:, feature_mask], 
                             y_test, **modelparams)
        else:
            result = validate_switch(loo_flag, model, x_train[:, feature_mask], 
                             y_train, **modelparams)
        # results.append([max_feature]+ list(modelparams.values()) + [result["loo"]["r2_score"]] +[result])
        result.update(dict(feature_mask=feature_mask))
        results.append(result)
    return results