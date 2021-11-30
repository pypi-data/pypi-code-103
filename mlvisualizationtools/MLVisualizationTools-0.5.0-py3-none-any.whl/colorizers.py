"""
Colorizers

A set of functions to apply colorization to a graphable dataset.
"""

from MLVisualizationTools.backend import GraphData
from MLVisualizationTools.types import ColorizerModes
from typing import Optional
import warnings

def _valid_colorization_call(data: GraphData, colorkey: str, apply_to_model: bool, apply_to_data: bool):
    """Internal function used to throw errors for invalid colorization calls"""
    locations = []
    if apply_to_model:
        locations.append(data.modeldata)
        if data.modeldata.colorized != ColorizerModes.NotColorized:
            warnings.warn("Colorization may overwrite existing colorization.")
    if apply_to_data:
        if data.datavalues is not None:
            locations.append(data.datavalues)
            if data.datavalues.colorized != ColorizerModes.NotColorized:
                warnings.warn("Colorization may overwrite existing colorization.")
        else:
            warnings.warn("Colorization should be applied to data values, but no data was given.")

    if len(locations) == 0:
        warnings.warn("Colorization not being applied to any points")

    if colorkey is not None:
        data.colorkey = colorkey
    data.check_color_key()

    return locations

def simple(data: GraphData, color: str, colorkey: Optional[str] = None,
           apply_to_model:bool = True, apply_to_data: bool = False) -> GraphData:
    """
    Marks all points as being the color inputted

    :param data: GraphData object from a model interface call
    :param color: Color that is applied
    :param colorkey: Overrides default 'Color' as a location to store color
    :param apply_to_model: Applies colorization to model predictions
    :param apply_to_data: Applies colorization to data values
    """

    locations = _valid_colorization_call(data, colorkey, apply_to_model, apply_to_data)

    for d in locations:
        df = d.dataframe

        df[data.colorkey] = color
        d.colorized = ColorizerModes.Simple
        d.basecolor.color = color

    return data

def binary(data: GraphData, highcontrast:bool=True, truecolor: Optional[str] = None, falsecolor: Optional[str] = None,
           cutoff:float=0.5, colorkey='Color', apply_to_model:bool = True, apply_to_data:bool = False) -> GraphData:
    """
    Colors grid based on whether the value is higher than the cutoff. Default colors are green for true and red
    for false. Black will appear if an error occurs.

    :param data: GraphData object from a model interface call
    :param highcontrast: Switches default colors to blue for true and orange for false
    :param truecolor: Manually specify truecolor
    :param falsecolor: Manually specify falsecolor
    :param cutoff: Cutoff value, higher is true
    :param colorkey: Overrides default 'Color' as a location to store color
    :param apply_to_model: Applies colorization to model predictions
    :param apply_to_data: Applies colorization to data values
    """

    if truecolor is None:
        if not highcontrast:
            truecolor = "green"
        else:
            truecolor = "blue"
    if falsecolor is None:
        if not highcontrast:
            falsecolor = "red"
        else:
            falsecolor = "orange"

    locations = _valid_colorization_call(data, colorkey, apply_to_model, apply_to_data)

    for d in locations:
        df = d.dataframe

        df.loc[df[data.outputkey] > cutoff, data.colorkey] = truecolor
        df.loc[df[data.outputkey] <= cutoff, data.colorkey] = falsecolor
        d.colorized = ColorizerModes.Binary
        d.truecolor.color = truecolor
        d.falsecolor.color = falsecolor

    return data