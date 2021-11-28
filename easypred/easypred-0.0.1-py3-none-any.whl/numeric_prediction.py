"""Subclass of prediction specialized in representing numeric predictions, thus
a prediction where both fitted and real data are either ints or floats.

It allows to compute accuracy metrics that represent the distance between
the prediction and the real values."""
from typing import Union

import numpy as np
import pandas as pd

from easypred import Prediction


class NumericPrediction(Prediction):
    """Class to represent a numerical prediction.

    Attributes
    -------
    real_values: Union[np.ndarray, pd.Series, list]
        The array-like object containing the N real values.
    fitted_values: Union[np.ndarray, pd.Series, list]
        The array-like object of length N containing the fitted values.

    Properties
    -------
    mae : float
        Mean Absolute Error. Measure of error calculated as the sum of the
        absolute value residuals, divided by the number of observations.
    mape : float
        Mean Absolute Percentage Error. Measure of error calculated as the sum
        of the absolute value relative residuals, divided by the number of
        observations. The value is a float between 0 and 1.
    mse : float
        Mean Squared Error. Measure of error calculated as the sum of the
        squared residuals, divided by the number of observations.
    percentage_correctly_classified : float
        The decimal representing the percentage of elements for which fitted
        and real value coincide.
    pcc : float
        Alias for percentage_correctly_classified.
    rmse : float
        Root Mean Squared Error. It is the square root of the mse.
    r_squared : float
        R squared coefficient calculated as the square of the correlation
        coefficient between fitted and real values. The value is a float between
        0 and 1.
    """

    @property
    def r_squared(self) -> float:
        """Returns the r squared calculated as the square of the correlation
        coefficient. Also called 'Coefficient of Determination'.

        ref: https://en.wikipedia.org/wiki/Coefficient_of_determination"""
        return np.corrcoef(self.real_values, self.fitted_values)[0, 1] ** 2

    @property
    def mse(self) -> float:
        """Return the Mean Squared Error.

        ref: https://en.wikipedia.org/wiki/Mean_squared_error"""
        return np.mean(self.residuals(squared=True))

    @property
    def rmse(self) -> float:
        """Return the Root Mean Squared Error.

        ref: https://en.wikipedia.org/wiki/Root-mean-square_deviation"""
        return np.sqrt(self.mse)

    @property
    def mae(self) -> float:
        """Return the Mean Absolute Error.

        ref: https://en.wikipedia.org/wiki/Mean_absolute_error"""
        return np.mean(self.residuals(absolute=True))

    @property
    def mape(self) -> float:
        """Return the Mean Absolute Percentage Error.

        ref: https://en.wikipedia.org/wiki/Mean_absolute_percentage_error"""
        return np.mean(self.residuals(absolute=True, relative=True))

    def residuals(
        self,
        squared: bool = False,
        absolute: bool = False,
        relative: bool = False,
    ) -> Union[np.ndarray, pd.Series]:
        """Return an array with the difference between the real values and the
        fitted values.

        Parameters
        ----------
        squared : bool, optional
            If True, the residuals are squared, by default False.
        absolute : bool, optional
            If True, the residuals are taken in absolute value, by default False.
        relative : bool, optional
            If True, the residuals are divided by the real values to return
            a relative measure. By default False.

        Returns
        -------
        Union[np.ndarray, pd.Series]
            Numpy array or pandas series depending on the type of real_values and
            fitted_values. Its shape is (N,).
        """
        residuals = self.real_values - self.fitted_values
        if relative:
            residuals = residuals / self.real_values
        if squared:
            return residuals ** 2
        if absolute:
            return abs(residuals)
        return residuals

    def matches_tolerance(self, tolerance: float = 0.0) -> Union[np.ndarray, pd.Series]:
        """Return a boolean array of length N with True where the distance
        between the real values and the fitted values is inferior to a
        given parameter."""
        return abs(self.real_values - self.fitted_values) <= tolerance

    def as_dataframe(self) -> pd.DataFrame:
        """Return prediction as a dataframe containing various information over
        the prediction quality."""
        residuals = self.residuals()
        data = {
            "Fitted Values": self.fitted_values,
            "Real Values": self.real_values,
            "Prediction Matches": self.matches(),
            "Absolute Difference": residuals,
            "Relative Difference": residuals / self.real_values,
        }
        return pd.DataFrame(data)

    def describe(self) -> pd.DataFrame:
        """Return a dataframe containing some key information about the
        prediction."""
        return pd.DataFrame(
            {
                "N": [len(self)],
                "MSE": self.mse,
                "RMSE": self.rmse,
                "MAE": self.mae,
                "MAPE": self.mape,
                "R^2": self.r_squared,
            },
            index=["Value"],
        ).transpose()
