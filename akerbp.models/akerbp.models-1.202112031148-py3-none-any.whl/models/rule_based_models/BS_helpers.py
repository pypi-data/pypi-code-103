import numpy as np

### BS-related methods
def _number_BS_regions(df_):
    """
    Gives each BS region a number

    Args:
        df (pd.DataFrame): should include 'BS_jump' column (others will be ignored)

    Returns:
        df (pd.DataFrame): same as the input dataframe with the added "BS_region" column with dtype='int'
    """
    df = df_.copy()
    start_idx = df.index.min()
    df['BS_region'] = np.nan
    for rid, idx in enumerate(df[df['BS_jump']==1].index):
        end_idx = idx
        df.loc[range(start_idx, end_idx), 'BS_region'] = rid
        start_idx = end_idx
    df['BS_region'].fillna(0, inplace=True)
    return df

def find_BS_jumps(df_):
    """
    Finds points where BS changes

    Args:
        df (pd.DataFrame): should include 'BS' column (others will be ignored)

    Returns:
        df (pd.DataFrame): same as the input dataframe, with the added 'BS_jump' with dtype='bool'
    """
    df = df_.copy()
    #First find points where BS changes
    df['BS_jump'] = 0
    df.loc[df['BS'].diff(1).ne(0), 'BS_jump'] = 1
    #mark each BS region with an ID
    df = _number_BS_regions(df)
    return df

def flag_BS(df_well, y_pred=None, **kwargs):
    """
    Returns anomalous BS values

    Args:
        df_well (pd.DataFrame): [description]

    Returns:
        [type]: [description]
    """
    print('Method: bitsize...')
    bs_step_size = kwargs.get('bs_step_size', 10)
    df_well      = find_BS_jumps(df_well)
    bs_anomalies = []
    for _, v in df_well[df_well['BS_jump'] == 0].groupby((df_well['BS_jump'] != 0).cumsum()):
        if v.shape[0] < bs_step_size:
            bs_anomalies.extend(v.index.tolist())
    if y_pred is None:
        y_pred = df_well.copy()
    y_pred.loc[:, ['flag_bitsize_gen']] = 0
    y_pred.loc[bs_anomalies, ['flag_bitsize_gen']] = 1
    return y_pred
