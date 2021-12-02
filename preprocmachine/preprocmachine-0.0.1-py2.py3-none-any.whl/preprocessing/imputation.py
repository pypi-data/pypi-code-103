import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer, SimpleImputer
from ..utils.data import get_numeric_categorical_columns
from ..algorithms.linear_regression import lr_get_mse


def apply_KNN_Imputation(
    df, target, config={"n_neighbors": 2, "weights": "uniform"}, eval_method=lr_get_mse
):

    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)

    n_neighbors = config["n_neighbors"]
    weights = config["weights"]

    imputer = KNNImputer(n_neighbors=n_neighbors, weights=weights)
    imputed_arr = imputer.fit_transform(numeric_columns)
    imputed_df = pd.DataFrame(imputed_arr, columns=numeric_columns.columns)

    processed_dataset = pd.concat([imputed_df, categorical_columns], axis=1)

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")


def apply_Simple_Imputation(df, config={}):

    strategy = config["strategy"]
    missing_values = config["missing_values"]

    imputer = SimpleImputer(strategy=strategy, missing_values=missing_values)
    imputed_arr = imputer.fit_transform(df)
    imputed_df = pd.DataFrame(imputed_arr, columns=df.columns)

    return imputed_df


def apply_most_frequent_value_imputer(df, target, config={}, eval_method=lr_get_mse):
    config["strategy"] = "most_frequent"

    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    config["missing_values"] = np.nan
    imputed_numeric_columns = apply_Simple_Imputation(numeric_columns, config)
    if len(categorical_columns.columns) > 0:
        config["missing_values"] = "NaN"
        imputed_categorical_columns = apply_Simple_Imputation(
            categorical_columns, config
        )
    else:
        imputed_categorical_columns = categorical_columns

    processed_dataset = pd.concat(
        [imputed_numeric_columns, imputed_categorical_columns], axis=1
    )

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")


def apply_mean_imputer(df, target, config={}, eval_method=lr_get_mse):
    config["strategy"] = "mean"

    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    config["missing_values"] = np.nan
    imputed_numeric_columns = apply_Simple_Imputation(numeric_columns, config)

    processed_dataset = pd.concat(
        [imputed_numeric_columns, categorical_columns], axis=1
    )

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")


def apply_median_imputer(df, target, config={}, eval_method=lr_get_mse):
    config["strategy"] = "median"

    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    config["missing_values"] = np.nan
    imputed_numeric_columns = apply_Simple_Imputation(numeric_columns, config)

    processed_dataset = pd.concat(
        [imputed_numeric_columns, categorical_columns], axis=1
    )

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")
