from astropy.units import beam_angular_area
from astropy.units import Quantity
from astropy.units import Unit
from .units_functions import check_units
from typing import Union
import numpy as np


def beam_equivalencies(beam_area: Quantity = None, bmaj: Union[Quantity, float] = None, bmin: Union[Quantity, float] = None, unit: Unit = None):
    if beam_area is None and bmaj is not None and bmin is not None:
        b_area = np.pi * bmaj * bmin / (4. * np.log(2))
    elif beam_area is None and bmaj is None and bmin is None:
        raise ValueError("Input parameters cannot be None")

    if isinstance(beam_area, float) and unit is not None:
        b_area *= unit
    elif isinstance(beam_area, Quantity) and unit is not None:
        if beam_area.unit is None or beam_area.unit.is_unity():
            beam_area *= unit
        else:
            raise ValueError("Area cannot be unitless")
    else:
        raise ValueError("Area cannot be unitless")
    return beam_angular_area(beam_area)
