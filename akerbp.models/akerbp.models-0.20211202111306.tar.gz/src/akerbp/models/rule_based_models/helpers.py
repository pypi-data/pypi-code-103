import numpy as np
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns
import os
import akerbp.models.rule_based_models.crossplot_helpers as crossplot_helpers

def _make_col_dtype_lists(df):
    """
    Returns lists of numerical and categorical columns

    Args:
        df (pd.DataFrame): dataframe with columns to classify

    Returns:
        tuple: lists of numerical and categorical columns
    """
    num_cols = set(df._get_numeric_data().columns)
    cat_cols = list(set(df.columns) - set(num_cols))
    return list(num_cols), cat_cols

def _apply_metadata(df, **kwargs):
    """
    Applies specified metadata to data

    Args:
        df (pd.DataFrame): dataframe to apply metadata to

    Returns:
        tuple: pd.Dataframe after applying metadata, list of numerical columns and list of categorical columns
    """
    num_cols, cat_cols = _make_col_dtype_lists(df)
    num_filler         = kwargs.get('num_filler', None)
    cat_filler         = kwargs.get('cat_filler', None)
    if num_filler is not None:
        df.loc[:, num_cols] = df[num_cols].replace(to_replace=num_filler, value=np.nan)
    if cat_filler is not None:
        df.loc[:, cat_cols] = df[cat_cols].replace(to_replace=cat_filler, value=np.nan)
    return df, num_cols, cat_cols 

def _validate_features(X_pred_features, expected_curves):
    """
    Checks that provided and expected features are the same
    """
    if not X_pred_features.issubset(expected_curves):
        missing_features = list(expected_curves - X_pred_features)
        if len(missing_features) > 0:
            raise ValueError("Following features are expected but missing: {}".format(missing_features))
    if not expected_curves.issubset(X_pred_features):
        missing_features = list(X_pred_features - expected_curves)
        if len(missing_features) > 0:
            raise ValueError("Following features are expected but missing: {}".format(missing_features))

def _create_features(X_pred):
    """
    Creates features necessary for algorithms
    """
    if 'VP' not in X_pred.columns:
        X_pred.loc[:,'VP'] = 304.8 / X_pred['AC']
    if 'VS' not in X_pred.columns:
        X_pred.loc[:,'VS'] = 304.8 / X_pred['ACS']
    if 'AI' not in X_pred.columns:
        X_pred.loc[:,'AI'] = X_pred['DEN'] * ((304.8 / X_pred['AC'])**2)
    if 'VPVS' not in X_pred.columns:
        X_pred.loc[:,'VPVS'] = X_pred['VP'] / X_pred['VS']
    return X_pred

def fill_holes(df_, flag_col, limit=3):
    """
    Fill holes/include adjacent points to anoamlies as anomalies

    Args:
        df_ (pd.DataFrame): dataframe with the column to fill holes
        flag_col (string): column of df to fill holes
        limit (int, optional): how many samples to include as anomalye adjacent to anomalies. Defaults to 3.

    Returns:
        list: list of new values
    """
    tmp = df_.copy()
    tmp['filled'] = tmp[flag_col].replace(
        0, np.nan
        ).fillna(
            method='ffill',
            limit=limit
        ).fillna(
            method='bfill',
            limit=limit
        ).replace(np.nan, 0)
    return tmp.filled.values

#FIXME! move to crossplot_helpers
def get_crossplot_scores(df_well, logname, curves, y_pred, method,  **algo_params):
    """
    Returns scores for each sample

    Args:
        df_well (pd.DataFrame): dataframe with data from one well
        logname (str): log to which all curves will the crossploted against
        curves (list): list of curves to analyse
        y_pred (pd.DataFrame): dataframe with results per sample

    Returns:
        pd.DataFrame: y_pred with extra columns of scores
    """
    for y in curves:
        _, scores, idx  = crossplot_helpers.find_crossplot_scores(df_well, x=logname, y=y, **algo_params)
        for a_method in scores.keys():
            y_pred.loc[idx, '{}_{}_{}'.format(a_method, method, logname.lower())] = scores[a_method]
            y_pred['{}_{}_{}'.format(a_method, method,  logname.lower())].fillna(0, inplace=True)
    return y_pred

#FIXME! move to crossplot_helpers
def get_crossplot_anomalies(df_well, logname, curves, **algo_params):
    """
    Returns bool for each sample indicating anomaly or not

    Args:
        df_well (pd.DataFrame): dataframe with data from one well
        logname (str): log to which all curves will the crossploted against
        curves (list): list of curves to analyse

    Returns:
        pd.DataFrame: y_pred with extra columns of scores
    """
    anomalies = []
    for y in curves:
        tmp, _, _  = crossplot_helpers.find_crossplot_scores(df_well, x=logname, y=y, **algo_params)
        anomalies.extend(tmp)
    return anomalies

def expand_flags(df_well, flag_col, expansion_size=3):
    """
    Expands the flagged samples by expansion_size in each direction

    Args:
        df_well (pd.DataFrame): The input dataframe
        flag_col (str): Name of the 

    Returns:
        df_well (pd.DataFrame): input dataframe with updated flag_col
    """
    #get all available indices in the well dataframe
    well_idx = df_well.index.tolist()

    #then the flagged rows
    flag_idx = df_well[df_well[flag_col]==True].index.tolist()

    #Then find the flagged indices in the well
    flag_idx_idx = [well_idx.index(i) for i in flag_idx]
    
    for i in range(1, expansion_size):
        #check that the before and after indices are available in the well
        before_flag_idx_i = [well_idx[x-i] for x in flag_idx_idx if ((x-i)>=0) and (well_idx[x-i] in well_idx)]
        after_flag_idx_i  = [well_idx[x+i] for x in flag_idx_idx if ((x+i)<len(well_idx)) and (well_idx[x+i] in well_idx)]
        
        #update the flag_col
        df_well.loc[before_flag_idx_i, flag_col] = 1
        df_well.loc[after_flag_idx_i, flag_col]  = 1
        
    return df_well

def print_metrics(true, pred, ax=None, print_values=False, title=None, fig_name=None, plot_dir=None):
    """
    Plot confusion matrix with metrics of bad logs detection

    Args:
        true (pd.Series): true values
        pred (pd.Series): predicted values
        ax (list, optional): axes indices. Defaults to None.
        print_values (bool, optional): specify if printing is required with confusion matrix. Defaults to False.
        title (str, optional): specifies title for confusion matrix. Defaults to None.
    """
    recall = sklearn.metrics.recall_score(true, pred)
    prec   = sklearn.metrics.precision_score(true, pred)
    f1sc   = sklearn.metrics.f1_score(true, pred)

    conf_matrix = sklearn.metrics.confusion_matrix(true, pred)

    LABELS = [False, True]
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(5,5))
    sns.heatmap(conf_matrix, xticklabels=LABELS, yticklabels=LABELS, annot=True,  annot_kws={"fontsize":14}, fmt="d", ax=ax);
    
    if title is None:
        title = 'Confusion matrix'
    if print_values:
        title = f'{title} \n Recall = {recall:.3f} \n Precision = {prec:.3f} \n F1-score = {f1sc:.2f}'
    ax.set_title(title, {'size':'15'})
    ax.set_ylabel('Label', {'size':'18'})
    ax.set_xlabel('Predicted class', {'size':'18'})
    plt.tight_layout()
    if plot_dir is not None:
        plt.savefig(os.path.join(plot_dir, '{}.jpg'.format(fig_name)), dpi=150)