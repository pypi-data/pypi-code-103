# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
try:
    import pyspark.sql.functions as F
    from pyspark.ml.feature import QuantileDiscretizer
except ImportError as ie:
    pass

class TrainingDataStats():

    def __init__(self, feature_columns, categorical_columns, label_column, spark_df, constraint_set=None, summary_df=None):
        """
        Arguments:
            feature_columns:
                The columns used for training the model
            categorical_columns:
                The set of non-numeric columns from the feature columns
            label_column:
                The column to be predicted by the model
            spark_df:
                The Spark training data frame
            constraint_set:
                data_drift_constraints in json format. This value is optional.
            summary_df:
                summary stats data frame. The summary stats can be reused from the drift stats.
                This value is also optional
        """
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.spark_df = spark_df
        self.label_column = label_column
        self.constraint_set = constraint_set
        self.summary_df = summary_df

    def generate_explain_stats(self, num_bins=10):
        """
            Arguments:
                num_bins: The number of bins in which we want to seggregate the stats.
                        The more the bins, the better the Explanations.
                        The default value is 10
        """
        explainability_configuration = {}
        if not self.summary_df:
            numerical_columns = sorted(
            [column for column in self.feature_columns if column not in self.categorical_columns])
            self.summary_df = self.spark_df.select(numerical_columns).summary(
                ).toPandas().set_index("summary").astype(float)
        cols = self.spark_df.columns
        explainability_configuration["mins"] = self.get_values(cols, "min")
        explainability_configuration["maxs"] = self.get_values(cols, "max")
        explainability_configuration["base_values"] = self.get_values(cols, "50%")
        explainability_configuration["stds"] = self.get_values(cols, "stddev")
        explainability_configuration["categorical_columns"] = self.categorical_columns
        explainability_configuration["feature_columns"] = self.feature_columns
        categorical_counts = self.compute_categorical_counts()
        numeric_column_index = [self.feature_columns.index(
                x) for x in self.feature_columns if x not in self.categorical_columns]

        explainability_configuration["categorical_counts"] = categorical_counts
        d_bins = self.compute_bins(numeric_column_index, num_bins)
        explainability_configuration["d_bins"] = d_bins
        feature_values, feature_frequencies, d_means, d_stds, d_mins, d_maxs = self.compute_bin_stats(numeric_column_index, num_bins)
        explainability_configuration["feature_values"] = feature_values
        explainability_configuration["feature_frequencies"] = feature_frequencies
        explainability_configuration["d_means"] = d_means
        explainability_configuration["d_stds"] = d_stds
        explainability_configuration["d_mins"] = d_mins
        explainability_configuration["d_maxs"] = d_maxs

        class_labels = [x[self.label_column]
                    for x in self.spark_df.select(self.label_column).distinct().collect()]
        explainability_configuration["class_labels"] = class_labels
        self.__compute_categorical_stats(explainability_configuration, categorical_counts, feature_values, feature_frequencies)
        return explainability_configuration
    
    def get_values(self, cols, key):
        key_values = self.summary_df.loc[key]
        key_values_dict = key_values.to_dict()
        return_values = {}
        for col, value in key_values_dict.items():
            if col in self.categorical_columns:
                continue
            return_values[cols.index(col)] = value
        return return_values

    def compute_categorical_counts(self):
        categorical_counts = {}
        categorical_column_index = [
                self.feature_columns.index(x) for x in self.categorical_columns]
        if self.constraint_set:
            constraints = self.constraint_set["data_constraints"]["constraints"]
            for constraint in constraints:
                if constraint["kind"] == "single_column":
                    col = constraint["columns"][0]
                    if col in self.categorical_columns:
                        index = self.feature_columns.index(col)
                        categorical_counts[str(index)] = constraint["content"]["frequency_distribution"]
        else:
            for index in categorical_column_index:
                col = self.feature_columns[index]
                values = self.spark_df.groupBy(col).count().collect()
                categorical_counts[str(index)] = {val[0]: val[1] for val in values}
        return categorical_counts

    def compute_bins(self, numeric_column_index, num_bins):
        d_bins = {}
        prob_array = []
        temp = 0
        # Compute the probability array as per the num_bins. 
        # For example, if num_bins=4, the prob_array will be [0.25, 0.5, 0.75, 1]
        # Implying every 25th percentile
        for i in range(num_bins):
            temp += 1/num_bins
            prob_array.append(temp)
        # d_bins are calculated based on the prob_array computed above
        for index in numeric_column_index:
            numeric_feature = self.feature_columns[index]
            d_bins[str(index)] = self.spark_df.stat.approxQuantile(numeric_feature, prob_array, 0.000000000001)
        return d_bins

    def compute_bin_stats(self, numeric_column_index, num_bins):
        d_means = {}
        d_mins = {}
        d_maxs = {}
        d_stds = {}
        feature_frequencies = {}
        feature_values = {}
        for index in numeric_column_index:
            feature = self.feature_columns[index]
            outCol = "{}_{}".format(feature, "buckets")
            result_discretizer = QuantileDiscretizer(
                numBuckets=num_bins, inputCol=feature, outputCol=outCol, relativeError=0.000000000001).fit(self.spark_df).transform(self.spark_df)
            values = result_discretizer.groupBy(outCol).agg(F.count(feature).alias("count"), F.mean(feature).alias("mean"), F.stddev(
                feature).alias("stddev"), F.min(feature).alias("min"), F.max(feature).alias("max")).collect()
            details = [val.asDict() for val in values]
            new_details = sorted(details, key=lambda i: i[outCol])
            feature_values[str(index)] = [int(val[outCol]) for val in new_details]
            feature_frequencies[str(index)] = [val["count"] for val in new_details]
            d_means[str(index)] = [val["mean"] for val in new_details]
            d_stds[str(index)] = [val["stddev"] for val in new_details]
            d_mins[str(index)] = [val["min"] for val in new_details]
            d_maxs[str(index)] = [val["max"] for val in new_details]
        return feature_values, feature_frequencies, d_means, d_stds, d_mins, d_maxs

    def __compute_categorical_stats(self, explainability_configuration, categorical_counts, feature_values, feature_frequencies):
        base_values = explainability_configuration['base_values']
        change_base_values = False
        categorical_columns_encoding_mapping = {}
        for key, value in categorical_counts.items():
            sort_values = dict(
                sorted(value.items(), key=lambda i: i[1], reverse=True))
            categorical_columns_encoding_mapping[key] = list(sort_values.keys())

            if not hasattr(base_values, str(key)):
                base_values[str(
                    key)] = categorical_columns_encoding_mapping[key][0]
                change_base_values = True

            feature_frequencies[key] = list(sort_values.values())
            keys = list(sort_values.keys())
            feature_values[key] = [keys.index(val) for val in keys]

        if change_base_values:
            explainability_configuration['base_values'] = base_values
        explainability_configuration['categorical_columns_encoding_mapping'] = categorical_columns_encoding_mapping
        explainability_configuration['feature_frequencies'] = feature_frequencies
        explainability_configuration['feature_values'] = feature_values
