import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame, Series
from typing import Tuple, List
from akerbp.models.rule_based_models import helpers


# Flatline anomalies
def get_sig_outliers(df: DataFrame, th: float = 2.5) -> Tuple[List, List]:
    """
    Returns indices of anomalous values of resistivities and scores
    representing how far from the mean (in standard deviations) they are.

    Args:
        df (pd.Series): series with data to analyse
        th (float, optional): multiplied by the number of standard deviations.
        Defaults to 3.

    Returns:
        tuple: list of anomalous indices and scores
    """
    mu = df.mean()
    std = df.std()
    outliers = list(df[df > mu + th * std].index)
    scores = abs((df - mu) / std).values.tolist()
    return outliers, scores


def get_resistivity_outliers(df_well: Series, method: str, th: float) -> Tuple[List, List]:
    """
    Returns outliers indices and scores for given series.

    Args:
        df_well (Series): series with values to find outliers
        method (str): get outliers from the derivative or variance
        th (float): number of standard deviations to consider an outlier

    Returns:
        Tuple: list of outliers indices and list of scores for all samples
    """
    if method == "derivative":
        df = pd.Series(np.abs(np.gradient(df_well)), index=df_well.index)
    elif method == "variance":
        df = pd.Series(
            df_well.rolling(window=5, center=True).var(), index=df_well.index
        )
    df_nona = df[df != 0].dropna()
    if len(df_nona) == 0:
        return [], np.zeros(len(df_well))
    outliers, scores = get_sig_outliers(df_nona, th=th)
    df_scores = pd.Series(np.zeros(len(df_well)), index=df_well.index)
    df_scores.loc[df_nona.index] = scores
    return outliers, df_scores.values


def flag_resistivities(df_well, y_pred=None, **kwargs):
    """
    Flag all resistivities outliers in the given data based on mean+th*std.

    Args:
        df_well (DataFrame): dataframe with resistivities columns
        y_pred (DataFrame, optional): dataframe with outputs to add new outputs.
        Defaults to None.

    Returns:
        DataFrame: dataframe with output columns
    """
    print("Method: resistivities...")
    cols = kwargs.get("cols", ["RDEP", "RMED", "RSHA", "RMIC"])
    cols = [c for c in cols if c in df_well.columns]
    if y_pred is None:
        y_pred = df_well.copy()
    for method in ["derivative", "variance"]:
        flag_cols = [f"flag_{method}_{c.lower()}" for c in cols]
        y_pred.loc[:, flag_cols] = 0
        for c in cols:
            sig_idx, scores = get_resistivity_outliers(
                df_well[c], method, th=2.7
            )
            y_pred.loc[sig_idx, [f"flag_{method}_{c.lower()}"]] = 1
            # include two samples before and after as anomalies as well
            y_pred[f"flag_{method}_{c.lower()}"] = helpers.fill_holes(
                y_pred,
                f"flag_{method}_{c.lower()}",
                limit=2
            )
            y_pred[f"agg_{method}_{c.lower()}"] = scores
    return y_pred
