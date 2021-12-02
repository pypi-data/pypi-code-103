import pandas as pd
from sklearn.preprocessing import MinMaxScaler, QuantileTransformer, StandardScaler
from ..utils.data import get_numeric_categorical_columns
from ..algorithms.linear_regression import lr_get_mse


def apply_Min_Max_Normalization(df, target, config={}, eval_method=lr_get_mse):

    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    target_column = numeric_columns.loc[:, target]
    nontarget_columns = numeric_columns.loc[:, numeric_columns.columns != target]

    normalizer = MinMaxScaler().fit(nontarget_columns)
    normalized_arr = normalizer.transform(nontarget_columns)
    normalized_df = pd.DataFrame(normalized_arr, columns=nontarget_columns.columns)

    processed_dataset = pd.concat(
        [normalized_df, categorical_columns, target_column], axis=1
    )

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")


def apply_Quantile_Normalization(
    df, target, config={"n_quantiles": 10, "random_state": 0}, eval_method=lr_get_mse
):

    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    target_column = numeric_columns.loc[:, target]
    nontarget_columns = numeric_columns.loc[:, numeric_columns.columns != target]

    n_quantiles = config["n_quantiles"]
    random_state = config["random_state"]

    normalizer = QuantileTransformer(n_quantiles=n_quantiles, random_state=random_state)
    normalized_arr = normalizer.fit_transform(nontarget_columns)
    normalized_df = pd.DataFrame(normalized_arr, columns=nontarget_columns.columns)

    processed_dataset = pd.concat(
        [normalized_df, categorical_columns, target_column], axis=1
    )

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")


def apply_Z_Score_Normalization(df, target, config={}, eval_method=lr_get_mse):

    numeric_columns, categorical_columns = get_numeric_categorical_columns(df)
    target_column = numeric_columns.loc[:, target]
    nontarget_columns = numeric_columns.loc[:, numeric_columns.columns != target]
    normalizer = StandardScaler().fit(nontarget_columns)
    normalized_arr = normalizer.transform(nontarget_columns)
    normalized_df = pd.DataFrame(normalized_arr, columns=nontarget_columns.columns)

    processed_dataset = pd.concat(
        [normalized_df, categorical_columns, target_column], axis=1
    )

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")
