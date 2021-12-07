import pandas as pd
from timewarpy import sample_data


def load_energy_data():
    """Loads a multi-variate time series dataset from the timewarpy library
    for energy usage forecasting.

    Returns:
        pandas.DataFrame: time series dataset
    """
    return pd.read_csv(sample_data.__path__[0] + '/energydata_complete.csv')
