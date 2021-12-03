import numpy as np
from akerbp.models.rule_based_models import helpers
from akerbp.models.rule_based_models import BS_helpers
from pyod.utils.utility import standardizer #returns z-score

def get_outliers(df_well, y_pred=None):
    
    """
    Returns CALI-BS outliers
    
    Args:
        df_well (pd.DataFrame): well data
        y_pred (pd.DataFrame): dataframe with flags
    
    Returns:
        pd.DataFrame: y_pred with added flag columns
    """ 
    if 'CALI' in df_well.columns and 'BS' in df_well.columns:
        df_well.loc[:, 'CALI_BS'] = np.abs(df_well['CALI'] - df_well['BS'])

    x = 'CALI_BS'
    y = 'CALI_BS'
    algo_params = {
        'DBSCAN_eps': 0.02,
        'EliEnv_contamination': 0.01,
        'EliEnv_random_state': 0,
        'SVM_gamma': 'scale',
        'SVM_nu': 0.01,
        'IsoFor_n_estimators': 20,
        'IsoFor_contamination': 0.05,
        'IsoFor_random_state': 0
    }

    df_well = BS_helpers.find_BS_jumps(df_well)

    if y_pred is None:
        y_pred = df_well.copy()

    # return if too many BS regions (a couple of wells with non-standard values)
    if df_well['BS_region'].nunique() >= 10:
        return y_pred
    
    y_pred.loc[:, ['flag_washout_gen', 'flag_washout_den']] = 0, 0
    den_washout_anomalies = []

    for bsr in df_well['BS_region'].unique():
        df_gr = df_well[df_well['BS_region']==bsr].copy()
        if (df_gr[x].dropna().shape[0] != 0) and (df_gr[y].dropna().shape[0] != 0):
            y_scores = helpers.get_crossplot_scores(
                df_gr, 'CALI_BS', ['CALI_BS'], y_pred, 'washout', **algo_params   
            )
            y_pred[y_scores.columns] = y_scores
                    
            den_washout_anomalies.extend(
                helpers.get_crossplot_anomalies(
                    df_gr, 'CALI_BS', ['CALI_BS'], **algo_params   
                )
            )
    y_pred.loc[den_washout_anomalies, ['flag_washout_gen', 'flag_washout_den']] = 1

    return y_pred
        
def flag_washout(df_well, y_pred=None, **kwargs):
    """
    Returns anomalous CALI-BS

    Args:
        df_well (pd.DataFrame): well data 
        y_pred (pd.DataFrame): dataframe to add detection columns to

    Returns:
        pd.DataFrame: y_pred with the added columns
    """
    print('Method: washout...')

    y_pred = get_outliers(df_well, y_pred)
    rolling_window = kwargs.get('washout_rolling_window', 101)
    for bsr in y_pred['BS_region'].unique():
        df_gr = y_pred[y_pred['BS_region']==bsr].copy()
        rows_with_values = df_gr[df_gr['CALI'].isna()==False].index
        if len(rows_with_values):
            df_gr.loc[rows_with_values, 'CALI_std'] = df_gr.loc[rows_with_values, 'CALI'].rolling(rolling_window).std().fillna(0)
            y_pred.loc[rows_with_values, 'score_washout_gen'] = np.abs(standardizer(df_gr.loc[rows_with_values, 'CALI_std'].values.reshape(-1,1)))

    y_pred['score_washout_gen'].fillna(0, inplace=True)
    return y_pred