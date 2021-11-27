from __future__ import annotations
from abc import ABC
import astropy.units as un
from astropy.units import Unit
from astropy.units import Quantity
import numpy as np
from ..units import check_units
from ..units import beam_equivalencies
from .parameter import Parameter
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..base import Dataset


class Image(Parameter, ABC):
    def __init__(self, **kwargs):
        """
        Class that represents an image. Inherits from parameter.
        :param kwargs: Parameter arguments
        """
        super().__init__(**kwargs)

        if self.data is not None:
            if self.data.ndim == 2:
                self.imsize = [self.data.shape[0], self.data.shape[1]]
            elif self.data.ndim == 3:
                self.imsize = [self.data.shape[1], self.data.shape[2]]
            else:
                raise ValueError("The image dimensions should be greater than 1")

        if check_units(self.cellsize, un.rad):
            self.cellsize = self.cellsize.to(un.rad)
        else:
            raise ValueError("Units for cellsize should be in units of Angle")

    def transform_intensity_units(self, intensity: Quantity = None, beam_area: Quantity = None, unit: Unit = None):
        if intensity is not None and beam_area is not None and unit is not None:
            if beam_area.unit == self.pixel_area.unit:
                beam_equiv = beam_equivalencies(beam_area=beam_area / self.pixel_area, unit=unit)
            else:
                raise ValueError("Beam and image areas need to have same units")
            return intensity.to((un.Jy / unit), equivalencies=beam_equiv)
        else:
            raise ValueError("Intensity, beam_area and unit need to be different from None")

    def calculate_noise(self, measurements: Dataset = None) -> None:
        if measurements is None:
            pass
        else:
            if measurements.feed_kind is None:
                measurements.check_feed()

            if measurements.parhands_weight_sum > 0.0:
                parhands_noise = 0.5 * np.sqrt(1.0 / measurements.parhands_weight_sum)
            else:
                parhands_noise = 0.0

            if measurements.crossedhands_weight_sum > 0.0:
                crosshands_noise = 0.5 * np.sqrt(1.0 / measurements.crossedhands_weight_sum)
            else:
                crosshands_noise = 0.0

            if measurements.feed_kind == "linear":
                if self.name == "I" or self.name == "Q":
                    self.noise = parhands_noise * (un.Jy / un.beam)
                elif self.name == "U" or self.name == "V":
                    self.noise = crosshands_noise * (un.Jy / un.beam)

            elif measurements.feed_kind == "circular":
                if self.name == "I" or self.name == "V":
                    self.noise = parhands_noise * (un.Jy / un.beam)
                elif self.name == "Q" or self.name == "U":
                    self.noise = crosshands_noise * (un.Jy / un.beam)
