import numpy as np
import pandas as pd
from typing import Iterable, Dict, List
from pandas.core.frame import DataFrame

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import auc, roc_curve, roc_auc_score

from .. import exceptions

# class DataDict:
# def process_columns():
# if column_mapping:


def compute_intersection(cur_hist, ref_edge, cur_edge):
    lower_boundary = np.min(cur_edge[:10])
    upper_boundary = np.max(ref_edge[1:])
    idx = np.where(
        (cur_edge[:10] >= lower_boundary) & (cur_edge[:10] <= upper_boundary)
    )
    intersection = np.sum(cur_hist[idx])

    return intersection


def get_feature_types(feature_mapping: dict):
    if not isinstance(feature_mapping, dict):
        raise exceptions.NotofTypeDictionary(
            """Expected dictionary type for feature mappings"""
        )

    for key, val in feature_mapping.items():
        if val == "O":
            feature_mapping[key] = "str"
        else:
            feature_mapping[key] = str(val)
    return feature_mapping


def count_missing(data: Iterable):
    if not isinstance(data, np.ndarray):
        raise exceptions.NotofTypeArray("""Data is expected to be of type np.array""")
    return len(np.argwhere(np.isnan(data)))


def compute_feature_stats(
    reference_data: Iterable,
    current_data: Iterable,
    reference_label: str,
    current_label: str,
) -> Dict:

    """Computes the drift of a feature given reference and current datasets.
       Currently works with dataframes

    Args:
        Reference_data: Dataframe containing reference data.
        engine: Sqlaclhemy engine.
        registry_schema: Registry schema. This table schema is used to determine which registry is searched for an active id.
        pipeline_registry_schema: Pipeline registry table schema.
        pipeline_tracking_id: Optional unique id associated with a pipeline run
        code_link: Link to code repository

    Returns:
        Returns either "None" or a tracking id.
    
    """
    if not isinstance(reference_data, np.ndarray):
        reference_data = np.array(reference_data)

    if not isinstance(current_data, np.ndarray):
        current_data = np.array(current_data)

    # count number of missing records
    nbr_missing_records = count_missing(reference_data)
    percent_missing = round((nbr_missing_records / reference_data.shape[0]) * 100, 2)

    # Remove missing values
    reference_data = reference_data[~np.isnan(reference_data)]
    current_data = current_data[~np.isnan(current_data)]

    ref_hist, ref_edge = np.histogram(reference_data, density=True,)
    cur_hist, cur_edge = np.histogram(current_data, density=True,)
    intersection = compute_intersection(cur_hist, ref_edge, cur_edge)
    unique_values = len(np.unique(reference_data))

    results = {
        f"{reference_label}_histogram": {
            "hist": ref_hist.astype(np.float32).tolist(),
            "edges": ref_edge[1:].astype(np.float32).tolist(),
        },
        f"{current_label}_histogram": {
            "hist": cur_hist.astype(np.float32).tolist(),
            "edges": cur_edge[:10].astype(np.float32).tolist(),
        },
        "intersection": intersection,
        "missing_records": f"{nbr_missing_records}, {percent_missing}%",
        "unique": unique_values,
    }

    return results


def compute_log_reg_auc(x_train, y_train):

    # Create model
    log_reg = LogisticRegression()
    log_reg.fit(x_train, y_train)

    preds = log_reg.predict_proba(x_train)[::, 1]
    fpr, tpr, thresholds = roc_curve(y_train, preds, pos_label=1)
    auc_score = auc(fpr, tpr)

    return auc_score


def compute_drift_feature_importance(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    feature_list: List[str],
    target_feature: str = None,
):
    # if not type(reference_data) == pd.DataFrame:
    # raise exceptions.NotDataFrame(
    # """Reference and current data must be of type pd.DataFrame"""
    # )
    # target type can be reg, binary, multiclass

    if (
        not type(reference_data) == pd.DataFrame
        or not type(current_data) == pd.DataFrame
    ):
        raise exceptions.NotDataFrame(
            """Reference and current data must be of type pd.DataFrame"""
        )

    feature_importance_dict = {}

    # Run feature importance
    reference_data["target"] = 0
    current_data["target"] = 1

    df = pd.concat([reference_data, current_data])
    df.dropna(inplace=True)

    # Set X data
    x_train = df[feature_list]

    # y_train is the indicator between reference and current data
    y_train = df.pop("target")

    # Remove missing indices

    # Fit model and return importances
    log_reg = LogisticRegression()
    log_reg.fit(x_train, y_train)
    preds = log_reg.predict_proba(x_train)[::, 1]
    importances = log_reg.coef_[0]

    if not len(importances) == len(feature_list):
        raise exceptions.LengthMismatch(
            """Number of features and feature importances are not the same"""
        )

    for feature, importance in zip(feature_list, importances):
        auc = compute_log_reg_auc(x_train[feature].to_numpy().reshape(-1, 1), y_train)
        feature_importance_dict[feature] = {
            "feature_importance": importance,
            "feature_auc": auc,
        }

    if target_feature is not None:

        auc = compute_log_reg_auc(
            df[target_feature].to_numpy().reshape(-1, 1), y_train,
        )

        feature_importance_dict[target_feature] = {
            "feature_importance": None,
            "feature_auc": auc,
        }

    return feature_importance_dict

