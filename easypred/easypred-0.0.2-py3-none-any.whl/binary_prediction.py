"""Subclass of Prediction specialized in representing a binary prediction, thus
a prediction where both the fitted and real data attain at most two different
values.

It allows to compute accuracy metrics like true positive, true negative, etc."""
from typing import Any, Union

import numpy as np
import pandas as pd

from easypred import Prediction


class BinaryPrediction(Prediction):
    """Class to represent a binary prediction.

    Attributes
    -------
    fitted_values: Union[np.ndarray, pd.Series, list]
        The array-like object of length N containing the fitted values.
    real_values: Union[np.ndarray, pd.Series, list]
        The array-like object containing the N real values.
    value_positive: Any
        The value in the data that corresponds to 1 in the boolean logic.
        It is generally associated with the idea of "positive" or being in
        the "treatment" group. By default is 1.

    Properties
    -------
    false_negative_rate : float
        Ratio between the number of wrongly predicted negative and the total
        number of positives. It tells the percentage of positives falsely
        classified as negative.
    false_positive_rate : float
        Ratio between the number of wrongly predicted positive and the total
        number of negatives. It tells the percentage of negatives falsely
        classified as positive.
    negative_predicted_value : float
        Ratio between the number of correctly classified negative and the total
        number of predicted negative. It measures how accurate the negative
        predictions are.
    percentage_correctly_classified: float
        The decimal representing the percentage of elements for which fitted
        and real value coincide.
    pcc: float
        Alias for percentage_correctly_classified.
    positive_predicted_value : float
        The ratio between the number of correctly predicted positives
        and the total number predicted positives. It measures how accurate the
        positive predictions are.
    precision : float
        Alias fo positive_predicted_value.
    recall : float
        Alias for sensitivity.
    sensitivity : float
        The ratio between the correctly predicted positive and the total number
        of real positive. It measures how good the model is at detecting
        positives. Aliased as "recall".
    specificity : float
        The ratio between the correctly predicted negative and the total number
        of real negative. It measures how good the model is at detecting
        negatives.
    value_negative : Any
        The value that it is not the positive value.
    """

    def __init__(
        self,
        real_values: Union[np.ndarray, pd.Series, list],
        fitted_values: Union[np.ndarray, pd.Series, list],
        value_positive: Any = 1,
    ):
        """Class to represent a generic prediction.

        Arguments
        -------
        real_values: Union[np.ndarray, pd.Series, list]
            The array-like object containing the real values. It must have the same
            length of fitted_values. If list, it will be turned into np.array.
        fitted_values: Union[np.ndarray, pd.Series, list]
            The array-like object of length N containing the fitted values. If list,
            it will be turned into np.array.
        value_positive: Any
            The value in the data that corresponds to 1 in the boolean logic.
            It is generally associated with the idea of "positive" or being in
            the "treatment" group. By default is 1.
        """
        super().__init__(real_values=real_values, fitted_values=fitted_values)
        self.value_positive = value_positive

    @property
    def value_negative(self) -> Any:
        """Return the value that it is not the positive value."""
        other_only = self.real_values[self.real_values != self.value_positive]
        if isinstance(self.real_values, np.ndarray):
            return other_only[0].copy()
        return other_only.reset_index(drop=True)[0]

    @property
    def _pred_pos(self) -> Union[np.ndarray, pd.Series]:
        return self.fitted_values == self.value_positive

    @property
    def _pred_neg(self) -> Union[np.ndarray, pd.Series]:
        return self.fitted_values == self.value_negative

    @property
    def _real_pos(self) -> Union[np.ndarray, pd.Series]:
        return self.real_values == self.value_positive

    @property
    def _real_neg(self) -> Union[np.ndarray, pd.Series]:
        return self.real_values == self.value_negative

    @property
    def false_positive_rate(self) -> float:
        """Return the ratio between the number of false positives and the total
        number of real negatives.

        It tells the percentage of negatives falsely classified as positive."""
        false_positive = self._pred_pos & self._real_neg
        return false_positive.sum() / self._real_neg.sum()

    @property
    def false_negative_rate(self):
        """Return the ratio between the number of false negatives and the total
        number of real positives.

        It tells the percentage of positives falsely classified as negative."""
        false_negative = self._pred_neg & self._real_pos
        return false_negative.sum() / self._real_pos.sum()

    @property
    def sensitivity(self):
        """Return the ratio between the correctly predicted positives and the
        total number of real positives.

        It measures how good the model is in detecting real positives."""
        caught_positive = self._pred_pos & self._real_pos
        return caught_positive.sum() / self._real_pos.sum()

    # Defyining Alias
    recall = sensitivity

    @property
    def specificity(self):
        """Return the ratio between the correctly predicted negatives and the
        total number of real negatives.

        It measures how good the model is in detecting real negatives."""
        caught_negative = self._pred_neg & self._real_neg
        return caught_negative.sum() / self._real_neg.sum()

    @property
    def positive_predictive_value(self):
        """Return the ratio between the number of correctly predicted positives
        and the total number predicted positives.

        It measures how accurate the positive predictions are."""
        caught_positive = self._pred_pos & self._real_pos
        return caught_positive.sum() / self._pred_pos.sum()

    # Defyining Alias
    precision = positive_predictive_value

    @property
    def negative_predictive_value(self):
        """Return the ratio between the number of correctly classified negative
        and the total number of predicted negative.

        It measures how accurate the negative predictions are."""
        caught_negative = self._pred_neg & self._real_neg
        return caught_negative.sum() / self._pred_neg.sum()

    def confusion_matrix(
        self, relative: bool = False, as_dataframe: bool = False
    ) -> Union[np.ndarray, pd.DataFrame]:
        """Return the confusion matrix for the binary classification.

        The confusion matrix is a matrix with shape (2, 2) that classifies the
        predictions into four categories, each represented by one of its elements:
        - [0, 0] : negative classified as negative
        - [0, 1] : negative classified as positive
        - [1, 0] : positive classified as negative
        - [1, 1] : positive classified as positive

        Parameters
        ----------
        relative : bool, optional
            If True, absolute frequencies are replace by relative frequencies.
            By default False.
        as_dataframe : bool, optional
            If True, the matrix is returned as a pandas dataframe for better
            readability. Otherwise a numpy array is returned. By default False.

        Returns
        -------
        Union[np.ndarray, pd.DataFrame]
            If as_dataframe is False, return a numpy array of shape (2, 2).
            Otherwise return a pandas dataframe of the same shape.
        """
        pred_pos = self.fitted_values == self.value_positive
        pred_neg = self.fitted_values != self.value_positive
        real_pos = self.real_values == self.value_positive
        real_neg = self.real_values != self.value_positive

        conf_matrix = np.array(
            [
                [(pred_neg & real_neg).sum(), (pred_pos & real_neg).sum()],
                [(pred_neg & real_pos).sum(), (pred_pos & real_pos).sum()],
            ]
        )

        # Divide by total number of values to obtain relative frequencies
        if relative:
            conf_matrix = conf_matrix / len(self.fitted_values)

        if not as_dataframe:
            return conf_matrix
        return self._confusion_matrix_dataframe(conf_matrix)

    def _confusion_matrix_dataframe(self, conf_matrix: np.ndarray) -> pd.DataFrame:
        """Convert a numpy confusion matrix into a pandas dataframe and add
        index and columns labels."""
        conf_df = pd.DataFrame(conf_matrix)
        values = [self.value_negative, self.value_positive]
        conf_df.columns = [f"Pred {val}" for val in values]
        conf_df.index = [f"Real {val}" for val in values]
        return conf_df

    def describe(self) -> pd.DataFrame:
        """Return a dataframe containing some key information about the
        prediction."""
        basic_info = self._describe()
        new_info = pd.DataFrame(
            {
                "Sensitivity": self.sensitivity,
                "Specificity": self.specificity,
                "Positive PV": self.positive_predictive_value,
                "Negative PV": self.negative_predictive_value,
            },
            index=["Value"],
        ).transpose()
        return basic_info.append(new_info)
