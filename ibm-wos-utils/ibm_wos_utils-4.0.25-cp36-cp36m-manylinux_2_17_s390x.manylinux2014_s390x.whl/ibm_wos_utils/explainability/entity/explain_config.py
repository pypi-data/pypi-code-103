# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
import numpy as np

from ibm_wos_utils.explainability.entity.constants import InputDataType, ProblemType, ExplanationType, FeatureSelection


class ExplainConfig():
    """Explainability configuration containing the parameters required to run explanation."""

    def __init__(self, input_data_type, problem_type, feature_columns, categorical_columns=[], explanation_types=[ExplanationType.LIME.value], prediction_column="prediction", probability_column="probability", training_stats=None, features_count=None, perturbations_count=None, sample_around_instance=False, discretize_continuous=True, discretizer="quartile", kernel_width=None, kernel=None, bag_of_words=True, exclude_stopwords=False, ngrams=[1], image_segment_algo=None, schema={}, feature_selection="lasso_path"):
        """
        Arguments:
            input_data_type: 
                The type of input data. Possible values are "structured", "unstructured_text", "unstructured_image".
            problem_type: 
                The problem type. Possible values are "binary", "multiclass", "regression".
            feature_columns: 
                The list of feature columns.
            categorical_columns: 
                The list of categorical columns.
            explanation_types: 
                The list of explanations to compute. Possible values are "lime", "contrastive".
            prediction_column:
                The prediction column name
            probability_column:
                The probability column name
            training_stats: A dictionary having the details of training data 
                statistics.
            features_count: 
                The number of features to be returned in the explanation. Default value is 10.
            perturbations_count: 
                The number of perturbations to be used while generating local explanation. Default value is 5000 for structured, unstructured_text data types and 1000 for unstructured_image data type.
            sample_around_instance: 
                if True, will sample continuous features in perturbed samples from a normal centered at the instance being explained. Otherwise, the normal is centered on the mean of the feature data. Default is False. Used only if input data type is structured.
            discretize_continuous:
                If True, all non-categorical features will be discretized into quartiles. Default value is True. Used only if input data type is structured.
            discretizer: 
                The type of discretization. Possible values are "quartile", "decile", "entropy". Default value is "quartile". Used only if discretize_continuous is True and input data type is structured.
            kernel_width: 
                The kernel width for the exponential kernel. Default value is sqrt (number of columns) * 0.75. Used only if input data type is structured.
            kernel: 
                Similarity kernel that takes euclidean distances and kernel
                width as input and outputs weights in (0,1). Default is an exponential kernel. Used only if input data type is structured.
            bag_of_words:
                If True, a word is the same everywhere in the text - i.e. we will index multiple occurrences of the same word. If False, order matters, so that the same word will have different ids according to position. Default value is True. Used only if input data type is unstructured_text.
            exclude_stopwords:
                If True, the stop words are removed while generating explanation. Default value is False. Used only if input data type is unstructured_text.
            ngrams:
                The number of words in sequence to be considered while generating explanation. Possible values are [1], [2], [3] corresponding to unigram, bigram and trigram. Default value is [1] ie., unigram. Used only if input data type is unstructured_text.
            image_segment_algo:
                The type of image segmentation algorithm to use. Possible values are 'quickshift', 'slic'. Used only if input data type is unstructured_image.
            schema:
                The schema of the feature columns in a dict with key having feature name and value having data type. Eg: {'feature1': 'int', 'feature2': 'float', 'feature3': 'string'}. Possible data type values are int, float, string, bool.
            feature_selection:
                how to select num_features. options are:
                'forward_selection': iteratively add features to the model.
                    This is costly when num_features is high
                'highest_weights': selects the features that have the highest
                    product of absolute weight * original data point when
                    learning with all the features
                'lasso_path': chooses features based on the lasso
                    regularization path
                'none': uses all features, ignores num_features
                'auto': uses forward_selection if num_features <= 6, and
                    'highest_weights' otherwise.
        """
        self.input_data_type = input_data_type
        self.problem_type = problem_type
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.explanation_types = explanation_types
        self.prediction_column = prediction_column
        self.probability_column = probability_column
        self.training_stats = training_stats
        self.features_count = features_count
        self.perturbations_count = perturbations_count
        self.sample_around_instance = sample_around_instance
        self.discretize_continuous = discretize_continuous
        self.discretizer = discretizer
        self.kernel_width = kernel_width
        self.kernel = kernel
        self.bag_of_words = bag_of_words
        self.exclude_stopwords = exclude_stopwords
        self.ngrams = ngrams
        self.image_segment_algo = image_segment_algo
        self.schema = schema
        self.feature_selection = feature_selection

    @property
    def input_data_type(self):
        return self._input_data_type

    @input_data_type.setter
    def input_data_type(self, input_data_type):
        supported_types = [i.value for i in InputDataType]
        if input_data_type not in supported_types:
            raise ValueError("The input data type {0} is invalid. Valid types are {1}".format(
                input_data_type, supported_types))
        self._input_data_type = InputDataType(input_data_type)

    @property
    def problem_type(self):
        return self._problem_type

    @problem_type.setter
    def problem_type(self, problem_type):
        supported_types = [p.value for p in ProblemType]
        if problem_type not in supported_types:
            raise ValueError("The problem type {0} is invalid. Valid types are {1}".format(
                problem_type, supported_types))
        self._problem_type = ProblemType(problem_type)

    @property
    def explanation_types(self):
        return self._explanation_types

    @explanation_types.setter
    def explanation_types(self, explanation_types):
        supported_types = [e.value for e in ExplanationType]
        if not all(t in supported_types for t in explanation_types):
            raise ValueError("The explanation types {0} are invalid. Valid types are {1}".format(
                explanation_types, supported_types))

        self._explanation_types = [
            ExplanationType(e) for e in explanation_types]

    @property
    def training_stats(self):
        return self._training_stats

    @training_stats.setter
    def training_stats(self, training_stats):
        if self.input_data_type is InputDataType.STRUCTURED:
            self._training_stats = TrainingStats(
                training_stats, self.feature_columns, self.categorical_columns)
        else:
            self._training_stats = None

    @property
    def features_count(self):
        return self._features_count

    @features_count.setter
    def features_count(self, features_count):
        if features_count:
            self._features_count = int(features_count)
        else:
            self._features_count = 10

    @property
    def perturbations_count(self):
        return self._perturbations_count

    @perturbations_count.setter
    def perturbations_count(self, perturbations_count):
        if perturbations_count:
            self._perturbations_count = int(perturbations_count)
        else:
            self._perturbations_count = 1000 if self.input_data_type is InputDataType.IMAGE else 5000

    @property
    def sample_around_instance(self):
        return self._sample_around_instance

    @sample_around_instance.setter
    def sample_around_instance(self, sample_around_instance):
        if sample_around_instance is None:
            self._sample_around_instance = False
        else:
            self._sample_around_instance = bool(sample_around_instance)

    @property
    def discretize_continuous(self):
        return self._discretize_continuous

    @discretize_continuous.setter
    def discretize_continuous(self, discretize_continuous):
        if discretize_continuous is None:
            self._discretize_continuous = True
        else:
            self._discretize_continuous = bool(discretize_continuous)

    @property
    def discretizer(self):
        return self._discretizer

    @discretizer.setter
    def discretizer(self, discretizer):
        if discretizer is None:
            self._discretizer = "quartile"
        else:
            self._discretizer = str(discretizer)

    @property
    def feature_selection(self):
        return self._feature_selection

    @feature_selection.setter
    def feature_selection(self, feature_selection):
        if feature_selection is None:
            feature_selection = "auto"
        supported_types = [p.value for p in FeatureSelection]
        if feature_selection not in supported_types:
            raise ValueError("The feature selection value {0} is invalid. Valid types are {1}".format(
                feature_selection, supported_types))
        self._feature_selection = FeatureSelection(feature_selection)


class TrainingStats():
    def __init__(self, training_stats, feature_columns, categorical_columns):
        training_stats = training_stats or {}
        self.__validate_stats(training_stats)
        training_stats = self.__convert_stats(training_stats)

        self.d_means = training_stats.get("d_means")
        self.d_stds = training_stats.get("d_stds")
        self.d_mins = training_stats.get("d_mins")
        self.d_maxs = training_stats.get("d_maxs")
        self.d_bins = training_stats.get("d_bins")
        self.feature_values = training_stats.get("feature_values")
        self.feature_frequencies = training_stats.get(
            "feature_frequencies")
        self.class_labels = training_stats.get("class_labels")
        self.base_values = training_stats.get("base_values")
        self.stds = training_stats.get("stds")
        self.mins = training_stats.get("mins")
        self.maxs = training_stats.get("maxs")
        self.categorical_counts = training_stats.get("categorical_counts")

        self.cat_col_indexes = [feature_columns.index(
            c) for c in categorical_columns]
        self.cat_cols_encoding_map = training_stats.get(
            "categorical_columns_encoding_mapping")

    def get_lime_stats(self):
        """Get the statistics which are sent to lime"""
        return {"means": self.d_means,
                "stds": self.d_stds,
                "mins": self.d_mins,
                "maxs": self.d_maxs,
                "bins": self.d_bins,
                "feature_values": self.feature_values,
                "feature_frequencies": self.feature_frequencies,
                "class_labels": self.class_labels}

    def get_cem_stats(self):
        """Get the statistics which are sent to cem"""
        cem_stats = {}

        base_values_list, sd_list, min_list, max_list = (
            [] for i in range(4))

        for i in range(len(self.base_values)):
            base_values_list.append(self.base_values.get(i))
            sd_list.append(self.stds.get(i) if self.stds.get(i) else 0)
            min_list.append(self.mins.get(i) if self.mins.get(i) else 0)
            max_list.append(self.maxs.get(i) if self.maxs.get(i) else 1)

        cem_stats["base_values"] = np.asarray(
            base_values_list, dtype=object)
        cem_stats["stds"] = np.asarray(sd_list, dtype=float)
        cem_stats["mins"] = np.asarray(
            [min_list], dtype=float)
        cem_stats["maxs"] = np.asarray(
            [max_list], dtype=float)

        if self.categorical_counts:
            cem_stats["categorical_counts"] = self.categorical_counts
        else:
            cem_stats["categorical_counts"] = {}

        return cem_stats

    def __validate_stats(self, training_stats):
        required_keys = ["d_means", "d_maxs", "d_mins", "d_stds", "d_bins",
                         "feature_values", "feature_frequencies", "class_labels", "base_values", "stds", "mins", "maxs", "categorical_counts", "categorical_columns_encoding_mapping"]

        provided_keys = training_stats.keys()
        if set(required_keys)-set(provided_keys):
            raise ValueError("The training stats is missing mandatory attributes. Missing attributes are {0}. Provided keys: {1}, Required keys: {2}".format(
                set(required_keys)-set(provided_keys), provided_keys, required_keys))

        for k in required_keys:
            if training_stats.get(k) is None:
                raise ValueError(
                    "The value of attribute {1} in training stats is invalid.".format(k))

    def __convert_stats(self, training_stats: dict):
        """Convert the keys in statistics dict from string to int and update categorical_columns_encoding_mapping"""
        stats = {}

        # Convert string keys to int
        for key in training_stats:
            key_details = training_stats.get(key)
            new_key_details = {}
            if(not isinstance(key_details, list)):
                for key_in_details in key_details:
                    new_key_details[int(key_in_details)
                                    ] = key_details[key_in_details]
            else:
                new_key_details = key_details
            stats[key] = new_key_details

        # Update categorical_columns_encoding_mapping
        updated_mapping = {}
        mapping_in_stats = stats.get(
            "categorical_columns_encoding_mapping")
        for cat_col in mapping_in_stats:
            updated_mapping[cat_col] = np.array(
                mapping_in_stats[cat_col])
        stats["categorical_columns_encoding_mapping"] = updated_mapping

        return stats
