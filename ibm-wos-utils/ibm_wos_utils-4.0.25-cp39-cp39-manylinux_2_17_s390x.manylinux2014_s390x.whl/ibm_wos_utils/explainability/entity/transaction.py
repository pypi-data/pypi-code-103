# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import numpy as np
from decimal import Decimal


class Transaction():
    """Transaction for which explanation needs to be computed."""

    def __init__(self, config, data_row):
        self.config = config
        self.data_row = data_row
        self.prediction = self.data_row.get(config.prediction_column)
        probabilities = self.data_row.get(config.probability_column)
        self.probability = max(probabilities) if probabilities else None

    def get_data_row(self):
        """Get the input data row as a list in order of model features"""
        data_row = []
        for feature_name in self.config.feature_columns:
            value = self.data_row.get(
                feature_name)
            if isinstance(value, Decimal):
                value = float(value)
            data_row.append(value)

        return np.asarray(data_row, dtype=np.object)

    def get_encoded_data_row(self):
        """Get the encoded data row by encoding the categorical columns."""
        updated_data_row = self.__get_updated_data_row()
        data_point = [updated_data_row.get(
            feature_name) for feature_name in self.config.feature_columns]

        # Encode categorical columns in data point
        for i in self.config.training_stats.cat_col_indexes:
            data_point[i] = self.config.training_stats.cat_cols_encoding_map[i].tolist().index(
                data_point[i])

        return np.asarray(data_point)

    def get_labels(self):
        """Get all the indexes with max probability value in probabilities array."""
        probabilities = self.data_row.get(self.config.probability_column)
        max_probability = np.max(probabilities)
        return [i for i, prob in enumerate(probabilities) if prob == max_probability]

    def __get_updated_data_row(self):
        """Method to replace None values for numeric columns and None/unknown values for categorical columns."""
        updated_data_row = self.data_row.copy()

        # For numeric columns, if the value in input data point is None, update it with max value from the training stats
        # For categorical columns, if the value in input data point is None or unseen value, update it with the categorical value with least frequency
        categorical_counts = self.config.training_stats.categorical_counts
        for k, v in updated_data_row.items():
            if k not in self.config.feature_columns:
                continue
            feature_index = self.config.feature_columns.index(k)

            if k in self.config.categorical_columns:
                cat_counts = categorical_counts[feature_index]
                if v is None or v not in cat_counts.keys():
                    updated_data_row[k] = min(cat_counts, key=cat_counts.get)
            else:
                if v is None:
                    updated_data_row[k] = self.config.training_stats.maxs.get(
                        feature_index)

        return updated_data_row
