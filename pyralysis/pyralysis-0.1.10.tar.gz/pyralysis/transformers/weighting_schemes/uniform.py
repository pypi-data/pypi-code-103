from abc import ABC
from ..wscheme import WeightingScheme


class Uniform(WeightingScheme, ABC):
    def __init__(self, **kwargs):
        """
        :param kwargs: WeightingScheme arguments
        """
        super().__init__(**kwargs)

    def transform(self) -> None:
        """
        This function calculates the uniform weights and transforms them according to this scheme,
        """
        if self.gridder is not None:
            dataset = self.input_data
            max_nu = dataset.max_nu
            for ms in dataset.ms_list:
                weight = ms.visibilities.weight
                idx, bin_count, w_k = self.gridder.grid_weights(ms, max_nu)
                weight /= w_k
        else:
            raise TypeError("gridding attribute cannot be None when calculting uniform weights")
