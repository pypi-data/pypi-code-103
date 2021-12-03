import numpy as np
import pandas as pd
from sklearn.covariance import EllipticEnvelope
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest

from pyod.utils.utility import standardizer #returns z-score


## Crossplot

def get_params(**kwargs):
    """
    Gets parameters for the outlier detection algorithms

    Returns:
        tuple: dictionaries with parameters per method
    """
    SVM_params = {
        'nu': kwargs.get('SVM_nu', 0.01)}
    IsoFor_params = {
        'n_estimators': kwargs.get('IsoFor_n_estimators', 50),
        'contamination': kwargs.get('IsoFor_contamination', 0.01),
        'random_state': kwargs.get('IsoFor_random_state', 0)
    }
    Abod_parameters = {
        'contamination': 0.1,
        'n_neighbors': 10
    }
    EliEnv_parameters = {
        'contamination': 0.05,
        'random_state': 0
    }
    return SVM_params, IsoFor_params, Abod_parameters, EliEnv_parameters

def find_crossplot_scores(df, x, y, algo='comb', **kwargs):
    """
    Find anomalies based on the crossplots of x vs. y

    Args:
        df_well (pd.DataFrame): dataframe with data from one well
        algo (str, optional): which algorithm to use. Defaults to 'comb'.

    Returns:
        list: list with indices of anomalous samples
    """
    algo = algo.lower()
    df  = df[(df[x]!=0) & (df[y]!=0)].copy()
    tmp = df[[x, y]].dropna().copy()

    anomal_idx = []
    method_scores = dict()
    return_scores = dict()
    SVM_params, IsoFor_params, Abod_parameters, EliEnv_parameters = get_params(**kwargs)
    
    #if there are not even 10 samples we return
    if len(tmp)<10:
        return [], {}, tmp.index

    if (algo=='comb'):
        elienv = EllipticEnvelope(
            contamination = EliEnv_parameters['contamination'],
            random_state = EliEnv_parameters['random_state']
        ).fit(tmp[[x, y]])
        preds2 = elienv.predict(tmp[[x, y]])
        if algo=='EliEnv':
            preds = preds2
        original_scores = elienv.score_samples(tmp[[x, y]])
        method_scores['EliEnv'] = np.abs(standardizer(original_scores.reshape(-1,1)))

    if (algo=='comb'):
        svm = OneClassSVM(
            kernel='rbf', 
            gamma='scale', 
            nu=SVM_params['nu']
        ).fit(tmp[[x, y]])
        preds3 = svm.predict(tmp[[x, y]])
        if algo=='svm':
            preds = preds3
        original_scores = svm.score_samples(tmp[[x, y]])
        method_scores['SVM'] = np.abs(standardizer(original_scores.reshape(-1,1)))

    if (algo=='comb'):
        ifo = IsolationForest(
            n_estimators=IsoFor_params['n_estimators'], 
            contamination=IsoFor_params['contamination'], 
            random_state=IsoFor_params['random_state']
        ).fit(tmp[[x, y]])
        preds4 = ifo.predict(tmp[[x, y]])

        if algo=='isofor':
            preds = preds4
        original_scores = ifo.score_samples(tmp[[x, y]])
        method_scores['IsoFor'] = standardizer(original_scores.reshape(-1,1))

    if algo=='comb':
        preds  = np.where(preds2==-1, 1, 0) +\
                np.where(preds3==-1, 1, 0) +\
                np.where(preds4==-1, 1, 0)
        tmp['pred'] = np.where(preds>1, 1, 0)
    else:
        tmp['pred'] = np.where(preds==-1, 1, 0)

    for k, v in method_scores.items():
        return_scores[k] = v[:,0]
    
    return_scores = pd.DataFrame(return_scores)
    return_scores['agg'] = return_scores.mean(axis=1)
    anomal_idx.append(list(tmp[tmp.pred==1].index))
    return sum(anomal_idx, []), return_scores, tmp.index

def train_crossplot(**kwargs):
    pass

def get_proba_predictions(X, y, bad_logs, model, cp_name):
    """
    Add to the dataframe the score results for each of the bad anomalies.

    Args:
        X (pd.DataFrame): dataframe for prediction on
        y (pd.DataFrame): datafrrame with columns to populate results
        bad_logs (pd.DataFrame): bad log samples dataframe
        models (dict): dictionary with models per cp
        cp_name (str): crossplot name

    Returns:
        y: pd.DataFrame populated with results
    """
    cp_preds = model.predict_proba(X)
    if cp_name == 'vp_den':
        y.loc[bad_logs.index, 'score_vpden_ac']  = cp_preds[:, 0]
        y.loc[bad_logs.index, 'score_vpden_den'] = cp_preds[:, 1]
    elif cp_name == 'vp_vs':
        y.loc[bad_logs.index, 'score_vpvs_ac']  = cp_preds[:, 0]
        y.loc[bad_logs.index, 'score_vpvs_acs'] = cp_preds[:, 1]
    elif cp_name == 'ai_vpvs':
        y.loc[bad_logs.index, 'score_aivpvs_ac']  = cp_preds[:, 0]
        y.loc[bad_logs.index, 'score_aivpvs_acs'] = cp_preds[:, 1]
        y.loc[bad_logs.index, 'score_aivpvs_den'] = cp_preds[:, 2]
    return y

def get_class_predictions(X, y, bad_logs, model, cp_name):
    """
    Add to the dataframe the class results for each of the bad anomalies.

    Args:
        X (pd.DataFrame): dataframe for prediction on
        y (pd.DataFrame): datafrrame with columns to populate results
        bad_logs (pd.DataFrame): bad log samples dataframe
        models (dict): dictionary with models per cp
        cp_name (str): crossplot name

    Returns:
        y: pd.DataFrame populated with results
    """
    cp_preds = model.predict(X)
    y['tmp'] = 0
    y.loc[bad_logs.index, 'tmp'] = cp_preds
    #Map predictions depending on which crossplot they come from
    if cp_name == 'vp_den':
        y.loc[y.tmp.isin([1,3]), 'flag_vpden_ac']  = 1
        y.loc[y.tmp.isin([2,3]), 'flag_vpden_den'] = 1        
    elif cp_name == 'vp_vs':
        y.loc[y.tmp.isin([1,3]), 'flag_vpvs_ac']  = 1
        y.loc[y.tmp.isin([2,3]), 'flag_vpvs_acs'] = 1 
    elif cp_name == 'ai_vpvs':
        y.loc[y.tmp.isin([4,5,6,7]), 'flag_aivpvs_den'] = 1
        y.loc[y.tmp.isin([1,3,5,7]), 'flag_aivpvs_ac']  = 1
        y.loc[y.tmp.isin([2,4,6,7]), 'flag_aivpvs_acs'] = 1
    return y

def flag_well_crossplots(X, x, y, algo, cp_name, **kwargs):
    """
    Returns anomalous indices of crossplots between x and y

    Args:
        X (pd.DataFrame): data of one well

    Returns:
        tuple: dataframe with scores and lists of anomalous indices
    """
    res = dict(zip(
        ['anomalies', 'scores', 'idx'],
        find_crossplot_scores(X, x, y, algo=algo, **kwargs)
    ))
    for comb_method, scs in res['scores'].items():
        method_col = '{}_{}'.format(comb_method, cp_name)
        X.loc[res['idx'], method_col] = scs.values
        X[method_col].fillna(0, inplace=True)
    return X, res['anomalies']

def flag_crossplots(X, x, y, algo, cp_name, **kwargs):
    """
    Returns anomalous indices of crossplots between x and y

    Args:
        X (pd.DataFrame): data of one well

    Returns:
        tuple: dataframe with scores and lists of anomalous indices
    """
    anomalies = []
    for lsu in X['GROUP'].unique():
        lsu_data = X[X['GROUP']==lsu]
        res = dict(zip(
            ['anomalies', 'scores', 'idx'],
            find_crossplot_scores(lsu_data, x, y, algo=algo, **kwargs)
        ))
        for comb_method, scs in res['scores'].items():
            method_col = '{}_{}'.format(comb_method, cp_name)
            X.loc[res['idx'], method_col] = scs.values
            X[method_col].fillna(0, inplace=True)
        anomalies.extend(res['anomalies'])
    return X, anomalies

def classify_badlog(y, cp_name, ds, key_wells, model):
    bad_logs = ds.df_original[ds.df_original['flag_crossplot_gen']!=0]
    # if no badlogs, dont do anything
    if len(bad_logs) == 0:
        return y
    df_preprocessed, _, feats = ds.preprocess(
        ds.df_original.loc[bad_logs.index],
        _normalize_curves={'key_wells':key_wells}
    )
    #scores
    y_scores = get_proba_predictions(df_preprocessed[feats], y, bad_logs, model, cp_name)
    y[y_scores.columns] = y_scores
    #flags
    y_flags = get_class_predictions(df_preprocessed[feats], y, bad_logs, model, cp_name)
    y[y_flags.columns] = y_flags
    return y

def flag_crossplot(X_pred, cp_names, datasets, models, key_wells, **kwargs):
    print('Method: crossplot - general...')
    outlier_methods = ['EliEnv', 'SVM', 'IsoFor'] #FIXME! The shouldn't preferably be hard-coded.
    for cp_name in cp_names:        
        for method in outlier_methods:
            X_pred['{}_{}'.format(method, cp_name)] = 0.

    #get anomalies per crossplot and their scores

    vp_den_anomalies, ai_vpvs_anomalies, vp_vs_anomalies = [], [], []
    
    X_pred, vp_den_anomalies  = flag_crossplots(X_pred, 'VP', 'DEN', 'comb', 'vp_den', **kwargs)

    X_pred, ai_vpvs_anomalies = flag_crossplots(X_pred, 'AI', 'VPVS', 'comb', 'ai_vpvs', **kwargs)

    X_pred, vp_vs_anomalies   = flag_crossplots(X_pred, 'VP', 'VS', 'comb', 'vp_vs', **kwargs)

    y = X_pred.copy()        
    y.loc[:, [
        'flag_vpden_ac', 'flag_vpvs_ac', 'flag_aivpvs_ac',
        'flag_vpvs_acs', 'flag_aivpvs_acs',
        'flag_vpden_den', 'flag_aivpvs_den'
    ]] = 0, 0, 0, 0, 0, 0, 0

    pred_gen_cols = ['flag_crossplot_gen', 'flag_vpden_gen', 'flag_aivpvs_gen', 'flag_vpvs_gen']
    y.loc[:, pred_gen_cols] = 0, 0, 0, 0        
    y.loc[vp_den_anomalies, ['flag_crossplot_gen', 'flag_vpden_gen']]   = 1
    y.loc[ai_vpvs_anomalies, ['flag_crossplot_gen', 'flag_aivpvs_gen']] = 1
    y.loc[vp_vs_anomalies, ['flag_crossplot_gen', 'flag_vpvs_gen']]     = 1

    #Add the general crossplot flags to X_pred(to use as features in the model)
    X_pred[pred_gen_cols] = y[pred_gen_cols]

    #Run the anomalous samples through the relevant trained model and get predictions
    #Preprocessing using key_wells will need the well_name column, but the value is unimportant
    X_pred['well_name'] = 'dummy'
    for cp_name in cp_names:
        print('Method: crossplot - {}...'.format(cp_name))
        ds = datasets[cp_name]
        ds.load_from_df(X_pred)
        y = classify_badlog(y, cp_name, ds, key_wells[cp_name], models[cp_name])
    y = y.fillna(0)

    return y
