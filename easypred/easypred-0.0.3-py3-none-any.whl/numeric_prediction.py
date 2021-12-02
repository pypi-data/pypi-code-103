"""Subclass of prediction specialized in representing numeric predictions, thus
a prediction where both fitted and real data are either ints or floats.

It allows to compute accuracy metrics that represent the distance between
the prediction and the real values."""
from typing import Union

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from easypred import Prediction


class NumericPrediction(Prediction):
    """Class to represent a numerical prediction.

    Attributes
    -------
    real_values: Union[np.ndarray, pd.Series, list]
        The array-like object containing the N real values.
    fitted_values: Union[np.ndarray, pd.Series, list]
        The array-like object of length N containing the fitted values.
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

    def plot_fit_residuals(
        self,
        figsize: tuple[int, int] = (20, 10),
        title_size: int = 14,
        axes_labels_size: int = 12,
        axs: Union[None, list[Axes]] = None,
        show_plot: bool = True,
    ) -> None:
        """Plot a two panels figure containing the plot of real against fitted
        values and the plot of residuals against fitted values.

        This method combines plot_fit and plot_residuals.

        These two graphs are useful in detecting potential biases in the
        prediction as they allow to detect deviations and clusters in the
        prediction.

        Parameters
        ----------
        figsize : tuple[int, int], optional
            Tuple of integers specifying the size of the plot. Default is
            (20, 10).
        title_size : int, optional
            Font size of the plots' titles. Default is 14.
        axes_labels_size : int, optional
            Font size of the axes labels. Default is 12.
        axs : list of matplotlib Axes, optional
            List of axes object of length 2 to draw the plot onto. Otherwise
            creates new Figure and Axes. Use this option to further customize ù
            the plot.
        show_plot : bool, optional
            If True, plot is showed using plt.show() from matplotlib. Used for
            testing purposes.

        Returns
        -------
        None
        """
        default_ax = False
        if axs is None:
            default_ax = True
            _, axs = plt.subplots(nrows=1, ncols=2, figsize=figsize)
            print(axs)

        self.plot_fit(
            title_size=title_size, axes_labels_size=axes_labels_size, ax=axs[0]
        )
        self.plot_residuals(
            title_size=title_size, axes_labels_size=axes_labels_size, ax=axs[1]
        )

        if default_ax & show_plot:
            plt.show()

    def plot_residuals(
        self,
        figsize: tuple[int, int] = (20, 10),
        hline: Union[int, None] = 0,
        title_size: int = 14,
        axes_labels_size: int = 12,
        ax: Union[None, Axes] = None,
        show_plot: bool = True,
    ) -> None:
        """Plot the scatterplot depicting the residuals against fitted values.

        Parameters
        ----------
        figsize : tuple[int, int], optional
            Tuple of integers specifying the size of the plot. Default is
            (20, 10).
        hline : int, optional
            Y coordinate of the red dashed line added to the scatterplot. If
            None, no line is drawn. By default is 0.
        title_size : int, optional
            Font size of the plot title. Default is 14.
        axes_labels_size : int, optional
            Font size of the axes labels. Default is 12.
        ax : matplotlib Axes, optional
            Axes object to draw the plot onto, otherwise creates new Figure
            and Axes. Use this option to further customize the plot.
        show_plot : bool, optional
            If True, plot is showed using plt.show() from matplotlib. Used for
            testing purposes.

        Returns
        -------
        None
        """
        default_ax = False
        if ax is None:
            default_ax = True
            _, ax = plt.subplots(figsize=figsize)

        ax.scatter(self.fitted_values, self.residuals())

        if hline is not None:
            ax.axhline(0, c="red", ls="--")

        ax.set_title("Residuals against fitted values", fontsize=title_size)
        ax.set_xlabel("Fitted values", fontsize=axes_labels_size)
        ax.set_ylabel("Residuals", fontsize=axes_labels_size)

        ax.grid(True, ls="--")

        if default_ax & show_plot:
            plt.show()

    def plot_fit(
        self,
        figsize: tuple[int, int] = (20, 10),
        line_slope: Union[int, None] = 1,
        title_size: int = 14,
        axes_labels_size: int = 12,
        ax: Union[None, Axes] = None,
        show_plot: bool = True,
    ) -> None:
        """Plot the scatterplot depicting real against fitted values.

        Parameters
        ----------
        figsize : tuple[int, int], optional
            Tuple of integers specifying the size of the plot. Default is
            (20, 10).
        line_slope : Union[int, None], optional
            Slope of the red dashed line added to the scatterplot. If None, no
            line is drawn. By default is 1, representing parity between real
            and fitted values.
        title_size : int, optional
            Font size of the plot title. Default is 14.
        axes_labels_size : int, optional
            Font size of the axes labels. Default is 12.
        ax : matplotlib Axes, optional
            Axes object to draw the plot onto, otherwise creates new Figure
            and Axes. Use this option to further customize the plot.
        show_plot : bool, optional
            If True, plot is showed using plt.show() from matplotlib. Used for
            testing purposes.

        Returns
        -------
        None
        """
        default_ax = False
        if ax is None:
            default_ax = True
            _, ax = plt.subplots(figsize=figsize)

        ax.scatter(self.fitted_values, self.real_values)

        if line_slope is not None:
            ax.axline((0, 0), slope=line_slope, c="red", ls="--")

        ax.set_title("Real against fitted values", fontsize=title_size)
        ax.set_xlabel("Fitted values", fontsize=axes_labels_size)
        ax.set_ylabel("Real values", fontsize=axes_labels_size)

        ax.grid(True, ls="--")

        if default_ax & show_plot:
            plt.show()
