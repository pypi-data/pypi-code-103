from abc import ABC
import dask.array as da
import numpy as np
from ..wscheme import WeightingScheme


class Robust(WeightingScheme, ABC):
    def __init__(self, robust_parameter: float = None, **kwargs):
        """
        :param robust_parameter: Briggs/Robust parameter
        :param kwargs: WeightingScheme arguments
        """
        super().__init__(**kwargs)
        self.robust_parameter = robust_parameter

    @property
    def robust_parameter(self):
        return self.__robust_parameter

    @robust_parameter.setter
    def robust_parameter(self, val):
        if -2.0 <= val <= 2.0:
            self.__robust_parameter = val
        else:
            raise ValueError("Robust parameter needs to be between [-2.0, 2.0]")

    def calculate_f2(self, sum_gridweights_squared, sum_weights, robust_parameter: float = None):
        """
        :param sum_gridweights_squared: Sum of the gridded weights squared
        :param sum_weights: Sum of the non-gridded weights
        :param robust_parameter: Robust/Briggs parameter
        :return: The f^2 term in the Briggs equation
        """
        if robust_parameter is None:
            robust_parameter = -1.0 * self.robust_parameter
        num = (5. * 10. ** robust_parameter) ** 2
        den = sum_gridweights_squared / sum_weights

        if den.any() == 0.0:
            raise ZeroDivisionError
        else:
            return num / den

    def transform(self) -> None:
        """
        This function calculates the robust weights and transforms them according to this scheme,
        """
        if self.gridder is not None:
            dataset = self.input_data
            max_nu = dataset.max_nu
            original_weight_sum = []
            gridded_weightsquared_sum = []
            for ms in dataset.ms_list:
                weight = ms.visibilities.weight
                idx, bin_count, w_k = self.gridder.grid_weights(ms, max_nu)
                original_weight_sum.append(da.sum(weight.data, axis=0))
                unique_idx = da.unique(idx).compute()
                gridded_weights = bin_count[unique_idx]  # Gridded weight for each u,v coordinate on the grid
                gridded_weightsquared_sum.append(da.sum(gridded_weights * gridded_weights, axis=0))

            original_weight_sum_array = da.array(original_weight_sum)
            gridded_weightsquared_sum_array = da.array(gridded_weightsquared_sum)
            original_weight_sum = da.sum(original_weight_sum_array, axis=0)
            gridded_weightsquared_sum = da.sum(gridded_weightsquared_sum_array, axis=0)

            f2 = self.calculate_f2(gridded_weightsquared_sum, original_weight_sum)

            for ms in dataset.ms_list:
                idx, bin_count, w_k = self.gridder.grid_weights(ms, max_nu)
                ms.visibilities.weight /= (1.0 + f2 * w_k)

        else:
            raise TypeError("gridding attribute cannot be None when calculting robust weights")
