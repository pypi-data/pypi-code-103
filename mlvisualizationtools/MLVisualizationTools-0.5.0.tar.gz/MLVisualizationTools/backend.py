import copy

from MLVisualizationTools.types import GraphDataTypes, ColorizerModes
from typing import List, Dict, Tuple, Optional
import warnings
import pandas as pd
from os import path

#Backend functions and classes used by the other scripts

def colinfo(data: pd.DataFrame, exclude:List[str] = None) -> Tuple[Dict[str, Dict], List[str]]:
    """
    Helper function for generating column info dict for a datframe

    :param data: A pandas Dataframe
    :param exclude: A list of data items to exclude
    """
    if exclude is None:
        exclude = []

    coldata = {}
    allcols = []
    for item in data.columns:
        if item not in exclude:
            coldata[item] = {'mean': data[item].mean(), 'min': data[item].min(), 'max': data[item].max()}
            allcols.append(item)
    return coldata, allcols

def fileloader(target: str, dynamic_model_version = True):
    """Specify a path relative to MLVisualizationTools"""
    if dynamic_model_version:
        if 'examples/Models' in target:
            import tensorflow as tf
            if float(tf.version.VERSION[:3]) < 2.5:
                target += "_v2.0"
    return path.dirname(__file__) + '/' + target

class ColorMessage:
    def __init__(self, color: Optional[str], message: str):
        self.color: Optional[str] = color
        self.message: str = message

class ColorizerableDataFrame:
    def __init__(self, dataframe: pd.DataFrame, mode: GraphDataTypes):
        self.dataframe: pd.DataFrame = dataframe

        self.colorized: ColorizerModes = ColorizerModes.NotColorized

        if mode == GraphDataTypes.ModelPrediction:
            self.basecolor = ColorMessage(None, 'Avg. Predictions from Model')
            self.truecolor = ColorMessage(None, 'Avg. Prediction is True')
            self.falsecolor = ColorMessage(None, 'Avg. Prediction is False')

        elif mode == GraphDataTypes.DataValues:
            self.basecolor = ColorMessage(None, 'Actual Data Values')
            self.truecolor = ColorMessage(None, 'Data Values are True')
            self.falsecolor = ColorMessage(None, 'Data Values are False')

        else:
            raise ValueError(str(mode) + " is not a valid data storage mode.")


class GraphData:
    def __init__(self, dataframe: pd.DataFrame, datatype: GraphDataTypes, steps: int, x: str,
                 y: str, anim: str = None, outputkey: str = 'Output'):
        """Class for holding information about grid or animation data to be graphed."""
        self.modeldata: ColorizerableDataFrame = ColorizerableDataFrame(dataframe, GraphDataTypes.ModelPrediction)
        self.datavalues: Optional[ColorizerableDataFrame] = None
        self.datatype: GraphDataTypes = datatype

        self.outputkey: str = outputkey
        self._colorkey: str = 'Color'
        self._sizekey: str = 'Size'

        self.steps: int = steps
        self.x: str = x
        self.y: str = y
        self.anim: Optional[str] = anim
        self.outputkey: str = outputkey

        self.orig_df_cols = copy.deepcopy(list(self.modeldata.dataframe.columns))

    def add_datavalues(self, dataframe: pd.DataFrame):
        self.datavalues = ColorizerableDataFrame(dataframe, GraphDataTypes.DataValues)
        self.orig_df_cols.append(copy.deepcopy(list(self.datavalues.dataframe.columns)))

    @property
    def colorkey(self):
        return self._colorkey

    @colorkey.setter
    def colorkey(self, value: str):
        self._colorkey = value
        self.check_color_key()

    @property
    def sizekey(self):
        return self._sizekey

    @sizekey.setter
    def sizekey(self, value: str):
        self._sizekey = value
        self.check_size_key()

    def check_color_key(self):
        if self._colorkey in self.orig_df_cols:
            warnings.warn(f"Color key '{self._colorkey}' was already in dataframe. This could mean that "
                          f"'{self._colorkey}' was a key in your dataset. This could result in data being overwritten. "
                          "You can pick a different key in the function call.")

    def check_size_key(self):
        if self._sizekey in self.orig_df_cols:
            warnings.warn(f"Size key '{self._sizekey}' was already in dataframe. This means that '{self._sizekey}' was "
                          "a key in your dataset. This could result in data being overwritten. You can pick a different"
                          " key in the function call.")