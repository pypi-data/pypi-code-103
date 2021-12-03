import numpy as np
from akerbp.models.rule_based_models import helpers
import akerbp.models.rule_based_models.crossplot_helpers as crossplot_helpers

def flag_outliers(df_well, y_pred=None, **kwargs):
    """
    Returns anomalous indices for AC, ACS and DEN based on outliers of crossplots between AC, ACS and DEN
    and other curves

    Args:
        df_well (pd.DataFrame): data from one well

    Returns:
        tuple: lists of anomalous indices of AC, ACS and DEN
    """
    print('Method: outliers...')
    if 'CALI_BS' not in df_well.columns:
        df_well['CALI_BS'] = np.abs(df_well['CALI'] - df_well['BS'])
    if 'RDEP_log' not in df_well.columns and 'RDEP' in df_well.columns:
        df_well['RDEP_log'] = np.log10(df_well.RDEP)
    default_curves = ['AC', 'ACS', 'CALI', 'GR', 'NEU', 'PEF', 'RDEP_log', 'CALI_BS']
    curves = kwargs.get('curves', default_curves)

    if 'GROUP' in curves:
        curves.remove('GROUP')

    algo_params = {
        'DBSCAN_eps': 0.4,
        'EliEnv_contamination': 0.01,
        'EliEnv_random_state': 0,
        'SVM_gamma': 'scale',
        'SVM_nu': 0.01,
        'IsoFor_n_estimators': 50,
        'IsoFor_contamination': 0.005,
        'IsoFor_random_state': 0
    }
    if y_pred is None:
        y_pred = df_well.copy()

    ac_outliers_anomalies = []
    acs_outliers_anomalies = []
    den_outliers_anomalies = []

    logname_curves = {
        'AC': ([c for c in curves if c not in ['VP', 'AC']], ac_outliers_anomalies),
        'ACS': ([c for c in curves if c not in ['VS', 'ACS']], acs_outliers_anomalies),
        'DEN': ([c for c in curves if c!='DEN'], den_outliers_anomalies)
        }

    method = 'outliers'
    for logname, (curves, anomalies) in logname_curves.items():
        for y in curves:
            flags, scores, idx  = crossplot_helpers.find_crossplot_scores(df_well, x=logname, y=y, **algo_params)
            anomalies.extend(flags)
            for a_method in scores.keys():
                y_pred.loc[idx, '{}_{}_{}'.format(a_method, method, logname.lower())] = scores[a_method]
                y_pred['{}_{}_{}'.format(a_method, method,  logname.lower())].fillna(0, inplace=True)

    y_pred.loc[:, ['flag_outliers_gen', 'flag_outliers_ac', 'flag_outliers_acs', 'flag_outliers_den']] =\
        0, 0, 0, 0
    y_pred.loc[ac_outliers_anomalies, 'flag_outliers_ac']   = 1
    y_pred.loc[acs_outliers_anomalies, 'flag_outliers_acs'] = 1
    y_pred.loc[den_outliers_anomalies, 'flag_outliers_den'] = 1

    y_pred['flag_outliers_ac']  = helpers.fill_holes(y_pred, 'flag_outliers_ac')
    y_pred['flag_outliers_acs'] = helpers.fill_holes(y_pred, 'flag_outliers_acs')
    y_pred['flag_outliers_den'] = helpers.fill_holes(y_pred, 'flag_outliers_den')

    y_pred.loc[((y_pred.flag_outliers_ac==1) | (y_pred.flag_outliers_acs==1) |\
        (y_pred.flag_outliers_den==1)), 'flag_outliers_gen']  = 1

    return y_pred
