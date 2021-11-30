# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import json
import pandas as pd
import numpy as np
from lime.lime_tabular import LimeTabularExplainer


class Perturbations():
    """Generates perturbations for lime tabluar explainer."""

    def __init__(self, training_stats: json, problem_type: str, perturbations_count=10000, discretize_continuous=True):
        """
        Arguments:
            training_stats:
                The Explainability training statistics
            problem_type:
                The problem type of the machine learning model. The value can be either regression, binary or multiclass
            perturbations_count:
                The number of pertubations to be generated
        """
        self.training_stats = self.__convert_stats(training_stats)
        self.mode = "regression" if problem_type == "regression" else "classification"
        self.perturbations_count = perturbations_count
        self.discretize_continuous = discretize_continuous
        self.__parse_training_stats()

    def __convert_stats(self, training_stats):
        """Convert the string number keys in stats to int"""
        updated_stats = {}
        for key, value in training_stats.items():
            if type(value) == dict:
                dict_value = {}
                for key1, value1 in value.items():
                    dict_value[int(key1)] = value1
                updated_stats[key] = dict_value
            else:
                updated_stats[key] = value
        return updated_stats

    def __parse_training_stats(self):
        self.feature_columns = self.training_stats.get("feature_columns")
        self.cat_features_indexes = [i for i, v in enumerate(
            self.feature_columns) if v in self.training_stats.get("categorical_columns")]
        self.cat_col_encoding_map = self.training_stats.get(
            "categorical_columns_encoding_mapping")
        self.training_data_stats = self.training_stats
        self.data = pd.DataFrame(
            np.zeros((1, len(self.feature_columns))), columns=self.feature_columns).values
        self.stats = {
            "means": self.training_stats.get("d_means"),
            "mins": self.training_stats.get("d_mins"),
            "maxs": self.training_stats.get("d_maxs"),
            "stds": self.training_stats.get("d_stds"),
            "feature_values": self.training_stats.get("feature_values"),
            "feature_frequencies": self.training_stats.get("feature_frequencies")
        }

    def __get_data_row(self):
        data_row = [0] * len(self.feature_columns)

        base_values = self.training_stats.get("base_values")
        for i in range(len(self.feature_columns)):
            data_row[i] = base_values[i]

        for i in self.cat_features_indexes:
            data_row[i] = self.cat_col_encoding_map[i].index(
                data_row[i])

        return data_row

    def generate_perturbations(self):
        data_row = self.__get_data_row()
        lime_tabular = LimeTabularExplainer(self.data,
                                            feature_names=np.asarray(self.feature_columns), categorical_features=self.cat_features_indexes,
                                            categorical_names=self.cat_col_encoding_map,
                                            mode=self.mode,
                                            random_state=10,
                                            training_data_stats=self.stats,
                                            discretize_continuous=self.discretize_continuous)
        _, response = lime_tabular._LimeTabularExplainer__data_inverse(
            np.array(data_row), self.perturbations_count)
        df = pd.DataFrame(response, columns=self.feature_columns)
        return self.__get_decoded_df(df)

    def __get_decoded_df(self, df):
        for key, value in self.cat_col_encoding_map.items():
            feature_value = df[self.feature_columns[key]]
            feature_value_decoded = [value[int(x)] for x in feature_value]
            df[self.feature_columns[key]] = pd.Series(feature_value_decoded)
        return df
