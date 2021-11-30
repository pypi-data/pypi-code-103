import numpy as np
import operator

def _add_inter_curves(df, curves, new_col_name, method='sub'):
    """
    Creates a feature given by a calculation between two curves

    Args:
        df (pd.DataFrame): dataframe with curves to calculate another curve from
        curves (list): strings list with curves names
        method (string, optional): which computation to do between the two curves. Defaults to 'sub'.

    Returns:
        tuple: pd.DataFrame with new column and new column name
    """
    cls_name = method
    try:
        cls = getattr(operator, cls_name)
    except AttributeError as ae:
        print(ae)
    op_cols = [new_col_name, method, curves[1]]
    df.loc[:, new_col_name] = cls(df[curves[0]], df[curves[1]])
    return df, op_cols

def _add_log_features(df, log_features):
    """
    Creates columns with log10 of curves

    Args:
        df (pd.DataFrame): dataframe with columns to calculate log10 from

    Returns:
        tuple: pd.DataFrame of new dataframe and list of names of new columns of log10
    """
    log_cols = [col+'_log' for col in log_features]
    for col in log_features:
        df_tmp = df[col].copy()
        df_tmp = df_tmp.clip(lower=0)
        df.loc[:, col+'_log'] = np.log10(df_tmp + 1)
    return df, log_cols

def _add_gradient_features(df, gradient_features):
    """
    Creates columns with gradient of curves

    Args:
        df (pd.DataFrame): dataframe with columns to calculate gradient from

    Returns:
        tuple: pd.DataFrame of new dataframe and list of names of new columns of gradient
    """
    gradient_cols = [col+'_gradient' for col in gradient_features]
    for col in gradient_features:
        df.loc[:, col+'_gradient'] = np.gradient(df[col])
    return df, gradient_cols

def _add_rolling_features(df, columns, window):
    """
    Creates columns with window/rolling features of curves

    Args:
        df (pd.DataFrame): dataframe with columns to calculate rolling features from
        columns (list, optional): columns to apply rolling features to. Defaults to None.

    Returns:
        tuple: pd.DataFrame of new dataframe and list of names of new columns of rolling features
    """
    mean_cols = [col+'_window_mean' for col in columns]
    min_cols  = [col+'_window_min' for col in columns]
    max_cols  = [col+'_window_max' for col in columns]
    for col in columns:
        df.loc[:, col+'_window_mean'] = df[col].rolling(center=False, window=window, min_periods=1).mean()
        df.loc[:, col+'_window_max']  = df[col].rolling(center=False, window=window, min_periods=1).max()
        df.loc[:, col+'_window_min']  = df[col].rolling(center=False, window=window, min_periods=1).min()
    window_cols = mean_cols + min_cols + max_cols
    return df, window_cols

def _add_time_features(df, cols, n):
    """
    Adds n past values of columns (for sequential models modelling).
    df (pandas.dataframe): dataframe to add time features to
    n (int): number of past values to include

    Args:
        df (pd.DataFrame): dataframe to add time features to
        n (int): number of time steps

    Returns:
        tuple: dataframe with added time feature columns and names of new columns
    """
    new_df = df.copy()
    all_time_cols = []
    for time_feat in range(1, n+1):
        time_cols = [f'{c}_{time_feat}' for c in cols]
        all_time_cols.append(time_cols)
        new_df[:, time_cols] = df[cols].shift(periods=time_feat)
    return new_df, sum(all_time_cols, [])
