import numpy as np


def create_univariate_windows(df, train_horizon, pred_horizon, column):
    """Given a pandas dataframe, this will create deep learning friendly
    matrices (X, y) with a given training and prediction length.

    Args:
        df (pandas.Dataframe): raw data with column names
        train_horizon (int): number of data points in each training observation of the X matrix
        pred_horizon (int): number of data points in each prediction observation of the y matrix
        column (str): column to use
    """
    # number of windows
    num_windows = df.shape[0] - train_horizon - pred_horizon + 1

    # allocate memory to numpy
    X = np.zeros([num_windows, train_horizon, 1])
    y = np.zeros([num_windows, pred_horizon])

    # create numpy object
    raw_data = df[[column]].to_numpy()

    # loop through the windows
    for i in range(num_windows):

        # store X and Y information
        X[i] = raw_data[i: i+train_horizon]
        y[i] = raw_data[i+train_horizon: i+train_horizon+pred_horizon].reshape(1, -1)[0]

    return X, y
