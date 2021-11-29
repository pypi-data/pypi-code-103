import logging
import pandas as pd
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted
DEFAULT_MODEL = LGBMClassifier


class AdHocBoost:

    def __init__(self, number_stages=2, stage_model_cls=DEFAULT_MODEL,
                 stage_model_hyper_param_sets=None, stage_proba_thresholds=None,
                 sample_weight_multipliers=None):
        """
        Init function.
        :param number_stages: The number of stages in the model.
        :type number_stages: int
        :param stage_model_cls: The model class to use for each stage's model.
        :type stage_model_cls: Any sklearn-like class with `.fit()`, `.predict()`, and `predict_proba()` implemented.
        :param stage_model_hyper_param_sets: List of dictionaries containing the hyperparameters for each model.
        :type stage_model_hyper_param_sets: list<dict<>>
        :param stage_proba_thresholds: List of probability thresholds for each stage's model.
        :type stage_proba_thresholds: list<float>
        :param sample_weight_multiplier: A scalar constant for multiplying class weights
        :type sample_weight_multiplier: float
        """

        # Load default parameters if necessary.
        if stage_proba_thresholds is None:
            stage_proba_thresholds = [1e-3]
        if sample_weight_multipliers is None:
            sample_weight_multipliers = [1.7, 1.7]
        if stage_model_hyper_param_sets is None:
            stage_model_hyper_param_sets = [
                {'learning_rate': 0.1762, 'min_data_in_leaf': 17, 'num_leaves': 29},
                {'learning_rate': 0.0352, 'min_data_in_leaf': 19, 'num_leaves': 33}]

        # Check validity of the input parameters.
        try:
            assert number_stages == len(stage_model_hyper_param_sets) and \
                   number_stages - 1 == len(stage_proba_thresholds) and \
                   number_stages == len(sample_weight_multipliers)
        except AssertionError as error:
            logging.error(f"{error}: Check number_stages, stage_model_hyper_param_sets, and stage_proba_thresholds; "
                          f"they disagree about number of stages in the model.")
            raise error

        # AdHocBoost uses some built-in sklearn functionality, so it needs to ascertain
        # Set the attributes from input parameters.
        self.number_stages = number_stages
        self.stage_model_cls = stage_model_cls
        self.stage_model_hyper_param_sets = stage_model_hyper_param_sets
        self.stage_proba_thresholds = stage_proba_thresholds
        self.sample_weight_multipliers = sample_weight_multipliers
        self.stage_models = [stage_model_cls(**hyper_param_set, objective="binary") for hyper_param_set in
                             self.stage_model_hyper_param_sets]

    @classmethod
    def preprocess_config(cls, config_dict):
        """
        Function for working more easily with hyperparameter optimization. Takes in a flat dictionary of config, and
        maps to the necessary config structure for model creation.

        :param config_dict: a flattened dict of config values
        :type config_dict: dict
        :return: config dict preprocessed for model creation

        Examples:
            >>> config_dict = {
                'number_stages': 2,
                'model_0__sample_weight_multiplier': 0.17,
                'model_0__learning_rate': 0.1,
                'model_0__num_leaves': 30,
                'model_0__min_data_in_leaf': 17,
                'stage_0__proba_threshold': 0.2,
                'model_1__sample_weight_multiplier': 0.10,
                'model_1__learning_rate': 0.05,
                'model_1__num_leaves': 26,
                'model_1__min_data_in_leaf': 15,
            }
            >>> preprocessed_config_dict = AdHocBoost.preprocess_config(config_dict)
            >>> print(preprocessed_config_dict)
            {'number_stages': 2,
             'sample_weight_multipliers': [0.17, 0.1],
             'stage_model_hyper_param_sets': [{'learning_rate': 0.1,
                                               'min_data_in_leaf': 17,
                                               'num_leaves': 30},
                                              {'learning_rate': 0.05,
                                               'min_data_in_leaf': 15,
                                               'num_leaves': 26}],
                                               'stage_proba_thresholds': [0.2]}
        """
        logging.info("Preprocessing parameters...")

        # Internal function for converting float hyperparameters to ints.
        def preprocess_integer_param(param, value):
            integer_params = {'num_leaves', 'min_data_in_leaf', 'n_estimators'}
            if param in integer_params:
                new_value = int(round(value))
                logging.info(f"Parameter preprocessing received {param}={value}. {param} must be an int, so the value "
                             f"was rounded to {new_value}.")
                return new_value
            else:
                return value

        # Internal function for getting number of stages from a flat config-dict of hyperparameters.
        def get_number_stages(config_dict):
            return 1 + max([int(key_component)
                            for key in config_dict.keys()
                            for key_component in key.split('_') if key_component.isdigit()])

        # Get the number of stages
        number_stages = get_number_stages(config_dict)

        # Create empty lists for storing the preprocessed parameters.
        sample_weight_multiplier_list = []
        proba_thresholds_list = []
        model_hyperparameters_list = []
        for stage_number in range(number_stages):

            # Pop and store the model-agnostic hyperparams.
            sample_weight_multiplier_list.append(config_dict.pop(f'model_{stage_number}__sample_weight_multiplier'))
            if stage_number < number_stages - 1:
                proba_threshold = config_dict.pop(f"stage_{stage_number}__proba_threshold")
                proba_thresholds_list.append(proba_threshold)

            # store the rest of the model hyperparams to hyperparam sets
            model_hyperparameter_bounds = {k.removeprefix(f"model_{stage_number}__"): v
                                           for k, v in config_dict.items() if f"model_{stage_number}__" in k}
            preprocessed_model_hyperparameter_bounds = {k: preprocess_integer_param(k, v)
                                                        for k, v in model_hyperparameter_bounds.items()}
            model_hyperparameters_list.append(preprocessed_model_hyperparameter_bounds)

        # return the preprocessed stuff.
        return {'number_stages': number_stages,
                'stage_model_hyper_param_sets': model_hyperparameters_list,
                'stage_proba_thresholds': proba_thresholds_list,
                'sample_weight_multipliers': sample_weight_multiplier_list}

    def fit(self, train_X, train_y):
        """
        Fit the model.
        :param train_X: The train feature-array, of shape (n-samples, n-features)
        :type train_X: numpy nd array
        :param train_y: The train label-array, of shape (n-samples,)
        :type train_y: numpy 1d array
        """

        # Create a dataframe for tracking the predicted probability of each model.
        logging.info(f"Fitting entire model pipeline.")
        stage_prediction_df = pd.DataFrame({
            # f"stage{stage_number}": np.zeros(len(train_X))
            f"stage{stage_number}": np.zeros(train_X.shape[0])
            for stage_number in range(self.number_stages)})

        # For each model, fit it, then do a prediction on the train data and log it to `stage_prediction_df`
        for stage_number in range(self.number_stages):

            # Get this stage's training data as whatever's left from the prior stage's model filtering.
            if stage_number == 0:
                stage_mask = np.ones(train_X.shape[0], dtype=bool)
            else:
                proba_threshold = self.get_stage_proba_threshold(stage_number - 1)
                logging.info(f"Getting all data for stage{stage_number}--filter predicted probabilities from "
                             f"stage{stage_number - 1} by threshold {proba_threshold}")
                stage_mask = (stage_prediction_df[f"stage{stage_number - 1}"] >
                              proba_threshold).to_numpy()

            # If the probability threshold has been set too high, then there's no data to train the second model.
            # Catch this case and exit the model training early.
            try:
                assert stage_mask.sum() > 0
            except AssertionError as e:
                logging.error(f"There is no data to train for stage {stage_number}, because it has all been filtered "
                              f"out. Consider lowering the probability thresholds of prior stages. Exiting fitting.")
                raise e

            # Fit the stage model.
            stage_sample_weight = self.get_sample_weight_column(
                train_y[stage_mask],
                positive_sample_multiplier=self.get_stage_sample_weight_multiplier(stage_number))
            self.fit_stage_model(
                train_X[stage_mask],
                train_y[stage_mask],
                stage_sample_weight,
                stage_number=stage_number)

            # Do a prediction on the train data and log it to `stage_prediction_df`. The prediction only needs to be run
            # on the stage_mask rows, hence the filter.
            stage_prediction = self.stage_predict_proba(train_X[stage_mask], stage_number)
            stage_prediction_df.loc[stage_mask, f"stage{stage_number}"] = stage_prediction

    def fit_stage_model(self, stage_train_X, stage_train_y, stage_sample_weight, stage_number=0):
        """
        Fits the stage_number'th model.
        :param stage_train_X: The train feature-array, of shape (n-samples, n-features)
        :type stage_train_X: numpy nd array
        :param stage_train_y: The train label-array, of shape (n-samples,)
        :type stage_train_y: numpy 1d array
        :param stage_sample_weight: A column of sample weights, of shape (n-samples,)
        :type stage_sample_weight: numpy 1d array
        :param stage_number: The stage number model that is being fit.
        :type stage_number: int
        :return:
        """
        logging.info(f"Fitting stage {stage_number} model with {stage_train_X.shape[0]} data points, "
                     f"weighting the positive class by {stage_sample_weight.max()}...")
        model = self.get_stage_model(stage_number)
        model.fit(
            stage_train_X,
            stage_train_y,
            sample_weight=stage_sample_weight)

    def get_sample_weight_column(self, y, positive_sample_multiplier=1.7):
        """
        Gets sample-weight column for use in fitting a model. The negative class is weighted as `1`, and the positive
        class is weighted as `positive_sample_multiplier * sqrt(|Positives| / |Negatives|)`.
        :param y: Array of labels.
        :type y: np.array
        :param positive_sample_multiplier: The scalar constant for multiplying class weight.
        :type positive_sample_multiplier: float
        :return:
        """
        base_true_weight = np.sqrt(
            (y == False).sum() /
            (y == True).sum()
        )
        sample_weight_column = np.ones(y.shape[0])
        sample_weight_column[y == 1] = positive_sample_multiplier * base_true_weight
        return sample_weight_column

    def stage_predict_proba(self, data, stage_number):
        logging.info(f"Predicting proba on stage {stage_number} ({data.shape[0]} data points)...")
        return self.get_stage_model(stage_number).predict_proba(data)[:, 1]

    def stage_predict(self, data, stage_number):
        logging.info(f"Predicting label on stage {stage_number} ({data.shape[0]} data points)...")
        return self.get_stage_model(stage_number).predict(data)

    def predict_proba(self, data, predict_labels=False):
        """
        Predict probabilities.
        :param data: A feature-array, of shape (n-samples, n-features)
        :type data: np.array
        :param predict: Boolean that indicates whether to predict labels or just predict probabilities.
        :type predict: bool
        :return: pd.Series of predictions (either labels or probabilities)
        """

        # Before predicting, check if the model has been fitted
        if not self.is_fitted():
            logging.error(f"Model is not completely fitted; cannot execute prediction.")
            raise NotFittedError

        # Create a dataframe for tracking the prediction from each stage.
        logging.info(f"Predicting {'label' if predict_labels else 'proba'} from entire model pipeline:")
        stage_prediction_df = pd.DataFrame({
            f"stage{stage_number}": np.zeros(data.shape[0])
            for stage_number in range(self.number_stages - 1)
        })
        stage_prediction_df[f"stage{self.number_stages - 1}"] = \
            np.zeros(data.shape[0], dtype=bool if predict_labels else float)

        # For each model, do a prediction on the data and log it to `stage_prediction_df`
        for stage_number in range(self.number_stages):

            # Get the stage's mask.
            if stage_number == 0:
                stage_mask = np.ones(data.shape[0], dtype=bool)
            else:
                proba_threshold = self.get_stage_proba_threshold(stage_number - 1)
                logging.info(
                    f"Getting all data for stage{stage_number}--filter predicted probabilities from "
                    f"stage{stage_number - 1} by threshold {proba_threshold}")
                stage_mask = (stage_prediction_df[f"stage{stage_number - 1}"] >
                              proba_threshold).to_numpy()

            # Do a prediction on the data and log it to `stage_prediction_df`. The prediction only needs to be run
            # on the stage_mask rows, hence the filter.
            if (stage_number == self.number_stages - 1) and (predict_labels == True):
                stage_prediction = self.stage_predict(data[stage_mask], stage_number)
            else:
                stage_prediction = self.stage_predict_proba(data[stage_mask], stage_number)
            stage_prediction_df.loc[stage_mask, f"stage{stage_number}"] = stage_prediction

        # Return the last stage's predictions.
        # To conform with sklearn api of returning array of shape (n_rows, n_classes), a column of zeros is appended to
        # the left of the predicted probabilities.
        predicted_probas = stage_prediction_df[f"stage{self.number_stages - 1}"].to_numpy().reshape((-1, 1))
        return np.hstack([np.zeros((predicted_probas.shape[0], 1)), predicted_probas])

    def predict(self, data):
        """
        Predict labels.
        :param data: A feature-array, of shape (n-samples, n-features)
        :type data: np.array
        :return: pd.Series of predicted labels
        """

        # Before predicting, check if the model has been fitted
        if not self.is_fitted():
            logging.error(f"Model is not completely fitted; cannot execute prediction.")
            raise NotFittedError

        # return prediction
        return self.predict_proba(data, predict_labels=True)

    def is_fitted(self) -> bool:
        """
        Helper function to check if the model has been completely trained or not.
        :return: bool
        """
        for model in self.stage_models:
            if not check_is_fitted(model):
                return False
        return True

    def get_stage_model(self, stage_number: int):
        """
        Get helper function; gets and returns the stage_number'th model.
        :param stage_number: Model to retrieve
        :type stage_number: int
        :return: A model of type self.stage_model_cls.
        """
        return self.stage_models[stage_number]

    def get_stage_sample_weight_multiplier(self, stage_number: int):
        """
        Getter helper function; gets and returns the stage_number'th sample_weight_multiplier.
        :param stage_number: Sample weight to retrieve
        :type stage_number: int
        :return: float
        """
        return self.sample_weight_multipliers[stage_number]

    def get_stage_proba_threshold(self, stage_number: int):
        """
        Getter helper function; gets and returns the stage_number'th probability threshold.
        :param stage_number: Model to retrieve
        :type stage_number: int
        :return: A model of type self.stage_model_cls.
        """
        return self.stage_proba_thresholds[stage_number]
