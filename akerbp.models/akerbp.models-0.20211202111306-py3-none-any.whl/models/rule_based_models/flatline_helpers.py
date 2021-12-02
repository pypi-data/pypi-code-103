import numpy as np

### Flatline anomalies
def get_constant_derivatives(df, logname, th=0.0005):
    """
    Returns indices of anomalous samples based on derivatives lower than a threshold

    Args:
        df (pd.DataFrame): dataframe with data to analyse
        logname (str): curve to be flagged, if any
        th (float, optional): threshold to which lower values will be considered constant. Defaults to 0.0005.

    Returns:
        list: indices of constant derivatives
    """
    df['d1']              = np.gradient(df[logname], df['DEPTH'])
    df['d2']              = np.gradient(df['d1'], df['DEPTH'])
    df['derivative']      = np.abs(df['d1']-df['d2'])
    df['cnst_derivative'] = df['derivative']<th
    return df[df['cnst_derivative']==True].index, df['derivative']

def get_constant_windows(df, logname, window_size=10, min_periods=5, th=0.0005):
    """
    Returns indices of anomalous samples based on derivatives lower than a threshold within a window

    Args:
        df (pd.DataFrame): dataframe with data to analyse
        logname (str): curve to be flagged, if any
        window_size (int): size of window
        min_periods (int): min_periods of rolling window
        th (float, optional): threshold to which lower values will be considered constant. Defaults to 0.0005.

    Returns:
        list: indices of constant derivatives
    """
    df['minw']        = df[logname].rolling(window_size, min_periods=min_periods, center=True).min()
    df['maxw']        = df[logname].rolling(window_size, min_periods=min_periods, center=True).max()
    df['window_derivative'] = np.abs(df['maxw']-df['minw'])
    df['cnst_window'] = df['window_derivative']<th
    return df[df['cnst_window']==True].index, df['window_derivative']

def get_den_flatlines(df, th=0.002):
    """
    Returns flatlines specifically for density, where threshold was decided empirically

    Args:
        df (pd.DataFrame): dataframe with data to analyse
        th (float, optional): threshold to which lower values will be considered constant. Defaults to 0.002.

    Returns:
        list: indices of anomalous density samples
    """
    if len(df['DEN']):
        df['DEN_flat'] = np.gradient(df['DEN'])
        idx = df[
            (np.abs(df['DEN_flat'].diff())<th) &\
            (np.abs(df['DEN_flat'].diff(-1))<th)
        ].index
    else:
        idx = []
    return idx

def get_flatlines(df, logname, cols, window=5, var_window=10, n_cols=2):
    """
    Returns indices of anomalous values indicating flatline badlog

    Args:
        df (pd.DataFrame): data to analyze
        logname (str): logname to find anomalies
        cols (list): list of curves to analyse logname against
        window (int, optional): window size for window constant derivatives. Defaults to 10.

    Returns:
        list: indices of flatlines anomlies
    """
    # get gradients and see if one gradient is not as small as at least three other curves
    cols_grad     = [c+'_gradient' for c in cols]
    gradient_flag = (df[f'{logname}_gradient']<df[f'{logname}_gradient'].rolling(var_window, center=True).std()) &\
                    (np.sum(df[cols_grad]>df[cols_grad].rolling(var_window, center=True).std(), axis=1)>n_cols)
    # get variance
    variance      = df[[logname]+cols].rolling(window).var()
    variance_flag = (variance[logname]<variance[logname].rolling(var_window, center=True).std()) &\
                    (np.sum(variance[cols]>variance[cols].rolling(var_window, center=True).std(), axis=1)>n_cols)
    # flatlines
    flatlines = gradient_flag | variance_flag
    return flatlines[flatlines==True].index

def find_start_end_indices(df_well):
    min_idx = df_well.index.max()
    max_idx = df_well.index.min()
    for col in ['AC', 'ACS', 'DEN']:
        min_idx = min(min_idx, df_well[df_well[col].notna()].index.min())
        max_idx = max(max_idx, df_well[df_well[col].notna()].index.max())
    return min_idx, max_idx

def flag_flatline(df_well, y_pred=None, **kwargs):
    """
    Returns flatlines indices for AC, ACS and DEN

    Args:
        df_well (pd.DataFrame): data from one well

    Returns:
        tuple: lists of gradient anomalies for AC, ACS and DEN
    """
    print('Method: flatline...')
    expected_curves = kwargs.get('expected_curves', set(['DEN', 'AC', 'ACS', 'GR', 'NEU', 'RDEP', 'RMED']))
    cols            = kwargs.get('cols', expected_curves)
    ncols           = kwargs.get('ncols', 2)

    for col in cols:
        df_well.loc[:, col+'_gradient'] = np.abs(np.gradient(df_well[col]))

    def run_get_flatlines(df_well, cols, ncols, **kwargs):
        window_size     = kwargs.get('window', 10)
        var_window_size = kwargs.get('var_window', 20)
        ac_grad_anomalies = get_flatlines(
            df=df_well, 
            logname='AC', 
            cols=list(set(cols) - set(['AC'])), 
            window=window_size,
            var_window=var_window_size,
            n_cols=ncols
        )
        acs_grad_anomalies = get_flatlines(
            df=df_well, 
            logname='ACS',
            cols=list(set(cols) - set(['ACS'])), 
            window=window_size,
            var_window=var_window_size,
            n_cols=ncols
        )
        den_grad_anomalies = get_flatlines(
            df=df_well, 
            logname='DEN', 
            cols=list(set(cols) - set(['DEN'])), 
            window=window_size,
            var_window=var_window_size,
            n_cols=ncols
        )
        return ac_grad_anomalies.tolist(), acs_grad_anomalies.tolist(), den_grad_anomalies.tolist()

    ac_grad_anomalies  = []
    acs_grad_anomalies = []
    den_grad_anomalies = []

    ac_flat_grad, ac_derivatives   = get_constant_derivatives(df_well, 'AC')
    acs_flat_grad, acs_derivatives = get_constant_derivatives(df_well, 'ACS')
    den_flat_grad, den_derivatives = get_constant_derivatives(df_well, 'DEN')

    ac_grad_anomalies.extend(ac_flat_grad)
    acs_grad_anomalies.extend(acs_flat_grad)
    den_grad_anomalies.extend(den_flat_grad)
    
    ac_flat_window, ac_window_grad   = get_constant_windows(df_well, 'AC')
    acs_flat_window, acs_window_grad = get_constant_windows(df_well, 'ACS')
    den_flat_window, den_window_grad = get_constant_windows(df_well, 'DEN')

    ac_grad_anomalies.extend(ac_flat_window)
    acs_grad_anomalies.extend(acs_flat_window)
    den_grad_anomalies.extend(den_flat_window)

    gen_grad_anomalies = []
    gen_grad_anomalies.extend(ac_grad_anomalies)
    gen_grad_anomalies.extend(acs_grad_anomalies)
    gen_grad_anomalies.extend(den_grad_anomalies)

    #run the function on points where there was constant window or gradient flags
    ac_grad_anomalies_main, acs_grad_anomalies_main, den_grad_anomalies_main = run_get_flatlines(
        df_well.loc[gen_grad_anomalies], cols, ncols, **kwargs)
    
    den_grad_anomalies_main.extend(get_den_flatlines(df_well.loc[gen_grad_anomalies]))
    
    #pick the start and end of well
    start_end_length = 50
    start_end_window_size = 2
    start_end_var_window_size = 2
    min_idx, max_idx = find_start_end_indices(df_well)
    start_condition = (df_well.index>=min_idx) & (df_well.index<=min_idx+start_end_length)
    end_condition = (df_well.index>=max_idx-start_end_length) & (df_well.index<=max_idx)

    #run the function for end points only with smaller window sizes
    df_well_ends = df_well[start_condition | end_condition]
    ac_grad_anomalies_ends, acs_grad_anomalies_ends, den_grad_anomalies_ends = run_get_flatlines(
        df_well_ends,
        cols,
        ncols,        
        **{'window': start_end_window_size, 'var_window': start_end_var_window_size}
        )

    ac_grad_anomalies_main.extend(ac_grad_anomalies_ends)
    acs_grad_anomalies_main.extend(acs_grad_anomalies_ends)
    den_grad_anomalies_main.extend(den_grad_anomalies_ends)

    if y_pred is None:
        y_pred = df_well.copy()

    y_pred.loc[:, ['flag_flatline_gen', 'flag_flatline_ac', 'flag_flatline_acs', 'flag_flatline_den']] =\
        0, 0, 0, 0

    #DEBUG   
    flag_columns = ['flag_den_only']
    lognames = ['ac', 'acs', 'den']
    for logname in lognames:
        flag_columns.extend([
            'flag_main_{}'.format(logname), 
            'flag_ends_{}'.format(logname), 
            'flag_derivs_{}'.format(logname), 
            'flag_windows_{}'.format(logname)
            ])
    y_pred.loc[:, flag_columns] = 0

    y_pred.loc[ac_grad_anomalies_main, ['flag_flatline_gen', 'flag_flatline_ac']]   = 1
    y_pred.loc[acs_grad_anomalies_main, ['flag_flatline_gen', 'flag_flatline_acs']] = 1
    y_pred.loc[den_grad_anomalies_main, ['flag_flatline_gen', 'flag_flatline_den']] = 1

    return y_pred