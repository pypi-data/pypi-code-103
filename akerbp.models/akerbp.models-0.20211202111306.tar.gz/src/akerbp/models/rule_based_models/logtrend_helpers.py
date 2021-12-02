import numpy as np
from akerbp.models.rule_based_models import helpers
import akerbp.models.rule_based_models.crossplot_helpers as crossplot_helpers

### Log trends
def flag_logtrend(df_well, y_pred=None, **kwargs):
    """
    Returns anomalous indices for AC, ACS and DEN based on log trends

    Args:
        df_well (pd.DataFrame): data from one well
        y_pred (pd.DataFrame): output data to attach results to
        score (bool): if returned values should be score or binary

    Returns:
        tuple: lists of anomalous indices of AC, ACS and DEN
    """
    print('Method: logtrend...')
    if 'CALI_BS' not in df_well.columns:
        df_well['CALI_BS'] = np.abs(df_well['CALI'] - df_well['BS'])
    default_curves = ['CALI', 'GR', 'NEU', 'CALI_BS']
    curves_to_diff = kwargs.get('curves_to_diff', default_curves)
    if 'GROUP' in curves_to_diff:
        curves_to_diff.remove('GROUP')
    
    algo_params = {
        'DBSCAN_eps': 0.1,
        'EliEnv_contamination': 0.01,
        'EliEnv_random_state': 0,
        'SVM_gamma': 'scale',
        'SVM_nu': 0.005,
        'IsoFor_n_estimators': 50,
        'IsoFor_contamination': 0.005,
        'IsoFor_random_state': 0
    }
    
    #replace curves values by difference of consecutive samples
    tmp_curves_to_diff = curves_to_diff +\
        [c for c in ['AC', 'ACS', 'DEN'] if c not in curves_to_diff]
    df_well[tmp_curves_to_diff] = df_well[tmp_curves_to_diff].diff()
    
    if y_pred is None:
        y_pred = df_well.copy()

    ac_trends_anomalies = []
    acs_trends_anomalies = []
    den_trends_anomalies = []

    logname_curves = {
        'AC': ([c for c in curves_to_diff if c not in ['VP', 'AC']], ac_trends_anomalies),
        'ACS': ([c for c in curves_to_diff if c not in ['VS', 'ACS']], acs_trends_anomalies),
        'DEN': ([c for c in curves_to_diff if c!='DEN'], den_trends_anomalies)
        }

    method = 'logtrend'
    for logname, (curves, anomalies) in logname_curves.items():
        for y in curves:
            flags, scores, idx  = crossplot_helpers.find_crossplot_scores(df_well, x=logname, y=y, **algo_params)
            anomalies.extend(flags)
            for a_method in scores.keys():
                y_pred.loc[idx, '{}_{}_{}'.format(a_method, method, logname.lower())] = scores[a_method]
                y_pred['{}_{}_{}'.format(a_method, method,  logname.lower())].fillna(0, inplace=True)

    y_pred.loc[:, ['flag_logtrend_gen', 'flag_logtrend_ac', 'flag_logtrend_acs', 'flag_logtrend_den']] =\
        0, 0, 0, 0
    y_pred.loc[ac_trends_anomalies, 'flag_logtrend_ac']   = 1
    y_pred.loc[acs_trends_anomalies, 'flag_logtrend_acs'] = 1
    y_pred.loc[den_trends_anomalies, 'flag_logtrend_den'] = 1

    y_pred['flag_logtrend_ac']  = helpers.fill_holes(y_pred, 'flag_logtrend_ac')
    y_pred['flag_logtrend_acs'] = helpers.fill_holes(y_pred, 'flag_logtrend_acs')
    y_pred['flag_logtrend_den'] = helpers.fill_holes(y_pred, 'flag_logtrend_den')

    y_pred.loc[((y_pred.flag_logtrend_ac==1) | (y_pred.flag_logtrend_acs==1) |\
        (y_pred.flag_logtrend_den==1)), 'flag_logtrend_gen']  = 1

    return y_pred
