import numpy as np
import pandas as pd
import umap as UMAP
from sklearn.preprocessing import MinMaxScaler

### UMAP
def umap3d(df_well, curves_umap):
    """
    Returns anomalous indices found by umap clustering.
    Not in use at the moment.

    Args:
        df_well (pd.DataFrame): data from one well
        curves_umap (list): list of curves to cluster

    Returns:
        list: list of anomalous indices
    """
    umap = UMAP.UMAP(n_components=3)
    df_well_umap = umap.fit_transform(MinMaxScaler().fit_transform(df_well[curves_umap]))
    df_well_umap = pd.DataFrame(df_well_umap, index=df_well.index, columns=['first', 'second', 'third'])
    tmp_X = df_well_umap[['first', 'second', 'third']]
    preds3 = OneClassSVM(gamma='scale', nu=0.001).fit_predict(tmp_X)
    preds4 = IsolationForest(n_estimators=50, contamination=0.001).fit_predict(tmp_X)
    preds  = np.where(preds3==-1, 1, 0) +\
                np.where(preds4==-1, 1, 0)
    tmp_X['pred'] = np.where(preds>0, True, False)
    return list(tmp_X[tmp_X.pred==True].index)

def flag_umap(df_well, y_pred=None, **kwargs):
    """
    Flags umap anomalies for AC, ACS and DEN

    Args:
        df_well ([type]): [description]

    Returns:
        [type]: [description]
    """
    print('Method: UMAP...')

    if y_pred is None:
        y_pred = df_well.copy()

    y_pred.loc[:, ['flag_umap_gen', 'flag_umap_ac', 'flag_umap_acs', 'flag_umap_den']] =\
        0, 0, 0, 0

    curves_umap = ['AC', 'GR', 'NEU', 'RDEP', 'RMED', 'VP', 'AI', 'VPVS']
    try:
        ac_umap = umap3d(df_well, curves_umap)    
    except:
        ac_umap = []  
    curves_umap = ['ACS', 'GR', 'NEU', 'RDEP', 'RMED', 'VS', 'AI', 'VPVS']
    try:
        acs_umap = umap3d(df_well, curves_umap)
    except:
        acs_umap = []
    curves_umap = ['GR', 'NEU', 'RDEP', 'RMED', 'AI', 'VPVS', 'DEN', 'DENC']
    try:
        den_umap = umap3d(df_well, curves_umap)
    except:
        den_umap = []

    y_pred.loc[ac_umap, ['flag_umap_gen', 'flag_umap_ac']]   = 1
    y_pred.loc[acs_umap, ['flag_umap_gen', 'flag_umap_acs']] = 1
    y_pred.loc[den_umap, ['flag_umap_gen', 'flag_umap_den']] = 1

    return y_pred