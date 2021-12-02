import pandas as pd
import numpy as np
from scipy import stats
from sklearn.neighbors import LocalOutlierFactor
from ..utils.data import get_numeric_categorical_columns
from ..algorithms.linear_regression import lr_get_mse


def apply_MAD_Score_Based_Outlier_Detection(
    df, target, config={"threshold": 3.0, "ratio": 0.3}, eval_method=lr_get_mse
):
    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    target_column = numeric_columns.loc[:, target]
    nontarget_columns = numeric_columns.loc[:, numeric_columns.columns != target]

    if df.isnull().values.any() > 0:
        return df, float("inf")

    median = nontarget_columns.apply(np.median, axis=0)

    # median_absolute_deviation = 1.4296 * \
    #     np.abs(nontarget_columns - median).apply(np.median, axis=0)
    median_absolute_deviation = stats.median_abs_deviation(nontarget_columns, scale=1)

    modified_z_scores = (nontarget_columns - median) / median_absolute_deviation

    outliers = nontarget_columns[np.abs(modified_z_scores) > config["threshold"]]

    to_drop = outliers[
        (outliers.count(axis=1) / outliers.shape[1]) > config["ratio"]
    ].index

    to_keep = set(nontarget_columns.index) - set(to_drop)

    if config["ratio"] == -1:
        filtered_df = nontarget_columns[
            ~(np.abs(modified_z_scores) > config["threshold"]).any(axis=1)
        ]
    else:
        filtered_df = nontarget_columns.loc[list(to_keep)]

    processed_dataset = pd.concat(
        [filtered_df, categorical_columns, target_column], axis=1
    )
    processed_dataset.dropna(inplace=True)

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")


def apply_Inter_Quantile_Range_Outlier_Detection(
    df, target, config={"ratio": 0.3}, eval_method=lr_get_mse
):
    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    target_column = numeric_columns.loc[:, target]
    nontarget_columns = numeric_columns.loc[:, numeric_columns.columns != target]

    if nontarget_columns.isnull().values.any() > 0:
        return df, float("inf")

    Q1 = nontarget_columns.quantile(0.25)
    Q3 = nontarget_columns.quantile(0.75)

    inter_quatile_range = Q3 - Q1

    outliers = nontarget_columns[
        (
            (nontarget_columns < (Q1 - 1.5 * inter_quatile_range))
            | (nontarget_columns > (Q3 + 1.5 * inter_quatile_range))
        )
    ]

    to_drop = outliers[
        (outliers.sum(axis=1) / outliers.shape[1]) > config["ratio"]
    ].index

    to_keep = set(nontarget_columns.index) - set(to_drop)

    if config["ratio"] == -1:
        filtered_df = nontarget_columns[~(filter_criteria).any(axis=1)]
    else:
        filtered_df = nontarget_columns.loc[list(to_keep)]

    processed_dataset = pd.concat(
        [filtered_df, categorical_columns, target_column], axis=1
    )
    processed_dataset.dropna(inplace=True)

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")


def apply_Local_Factor_Outlier_Detection(
    df,
    target,
    config={"n_neighbors": 4, "contamination": 0.1, "threshold": 30},
    eval_method=lr_get_mse,
):
    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    target_column = numeric_columns.loc[:, target]
    nontarget_columns = numeric_columns.loc[:, numeric_columns.columns != target]

    if nontarget_columns.isnull().values.any() > 0:
        return df, float("inf")

    clf = LocalOutlierFactor(n_neighbors=4, contamination=0.1)
    clf.fit_predict(nontarget_columns)

    LOF_scores = clf.negative_outlier_factor_

    k = config["threshold"]
    top_k_idx = np.argsort(LOF_scores)[-k:]
    top_k_values = [LOF_scores[i] for i in top_k_idx]

    filtered_df = nontarget_columns[LOF_scores < top_k_values[0]]

    processed_dataset = pd.concat(
        [filtered_df, categorical_columns, target_column], axis=1
    )
    processed_dataset.dropna(inplace=True)

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")
