import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.feature_selection import VarianceThreshold
from ..utils.data import get_numeric_categorical_columns
from ..algorithms.linear_regression import lr_get_mse


def apply_Missing_Ratio_Feature_Selection(
    df, target, config={"threshold": 0.2}, eval_method=lr_get_mse
):

    target_column = df.loc[:, target]
    nontarget_columns = df.loc[:, df.columns != target]

    missing_series = nontarget_columns.isnull().sum() / nontarget_columns.shape[0]

    missing_stats = pd.DataFrame(missing_series).rename(
        columns={"index": "feature", 0: "missing_fraction"}
    )

    # Sort with highest number of missing values on top
    missing_stats = missing_stats.sort_values("missing_fraction", ascending=False)

    # Find the columns with a missing percentage above the threshold
    record_missing = (
        pd.DataFrame(missing_series[missing_series > config["threshold"]])
        .reset_index()
        .rename(columns={"index": "feature", 0: "missing_fraction"})
    )

    to_drop = list(record_missing["feature"])
    to_keep = set(df.columns) - set(to_drop)

    processed_dataset = pd.concat([df[list(to_keep)], target_column], axis=1)

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")


def apply_K_Best_Feature_Selection(df, target, config={"k": 5}, eval_method=lr_get_mse):
    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    target_column = numeric_columns.loc[:, target]
    nontarget_columns = numeric_columns.loc[:, numeric_columns.columns != target]

    # Extract +ve columns
    lsv = list(nontarget_columns.lt(0).sum().values)
    lis = list(nontarget_columns.lt(0).sum().index)
    to_remove = []
    for i in range(0, len(lsv)):
        if lsv[i] > 0:
            to_remove.append(lis[i])
    lis = list(filter(lambda x: x not in to_remove, lis))

    selection = nontarget_columns
    if len(lis) > 0:
        filtered_df = nontarget_columns[lis]
        try:
            selector = SelectKBest(chi2, k=config["k"])
            selector.fit(filtered_df, target_column)

            cols = selector.get_support(indices=True)
        except:
            return df, float("inf")
        selection = filtered_df.iloc[:, cols]

    processed_dataset = pd.concat(
        [selection, categorical_columns, target_column], axis=1
    )

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")


def apply_Variance_Based_Feature_Selection(
    df, target, config={"threshold": 0}, eval_method=lr_get_mse
):
    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    target_column = numeric_columns.loc[:, target]
    nontarget_columns = numeric_columns.loc[:, numeric_columns.columns != target]

    selector = VarianceThreshold(threshold=config["threshold"])
    try:
        selector.fit(nontarget_columns, target_column)
        cols = selector.get_support(indices=True)
        selection = nontarget_columns.iloc[:, cols]
    except Exception as e:
        selection = nontarget_columns

    processed_dataset = pd.concat(
        [selection, categorical_columns, target_column], axis=1
    )

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")
