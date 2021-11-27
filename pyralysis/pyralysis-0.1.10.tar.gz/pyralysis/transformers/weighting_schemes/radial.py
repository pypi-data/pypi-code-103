from abc import ABC

from ..wscheme import WeightingScheme


class Radial(WeightingScheme, ABC):
    def __init__(self, use_w: bool = False, **kwargs):
        """
        Class that represents the Radial Weighting Scheme.
        :param use_w: Whether to use the w position to calculate the uv-distance
        :param kwargs: WeightingScheme arguments
        """
        super().__init__(**kwargs)
        self.use_w = use_w

    def transform(self) -> None:
        """
        This function calculates the radial weights and transforms them according to this scheme,
        """
        for ms in self.input_data.ms_list:
            dist = ms.visibilities.get_uvw_distance(self.use_w)
            weight = ms.visibilities.weight
            weight *= dist
