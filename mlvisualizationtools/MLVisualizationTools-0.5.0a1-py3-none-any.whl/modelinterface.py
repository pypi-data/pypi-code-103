"""
Model Interfaces

A set of functions to generate graphable data on how a ML model responds to input conditions.

Analytics functions can be called directly with a pandas dataframe, or indirectly through
the raw alternative, which takes a colinfo object.

Grid (3D) and Animation (4D) options are provided.
"""

from MLVisualizationTools.backend import colinfo, GraphData, GraphDataTypes
from MLVisualizationTools.modelanalytics import AnalyticsColumnInfo
from typing import List, Dict, Union
import pandas as pd
import warnings

#Functions for passing data to ml models

#region grid
def predictionGrid(model, x:Union[str, AnalyticsColumnInfo], y:Union[str, AnalyticsColumnInfo],
                   data:pd.DataFrame, exclude:List[str] = None, steps:int=20,
                   outputkey: str = 'Output') -> GraphData:
    """
    Creates a dataset from a 2d prediction on a ML model. Wrapper function for PredictionGridRaw()
    that automatically handles column info generation.

    :param model: A ML model
    :param x: xaxis for graph data
    :param y: yaxis for graph data
    :param data: A pandas dataframe
    :param exclude: Values to be excluded from data, useful for output values
    :param steps: Resolution to scan model with
    :param outputkey: Used to override default output name
    """
    coldata, allcols = colinfo(data, exclude)
    return predictionGridRaw(model, x, y, coldata, allcols, steps, outputkey)

def predictionGridRaw(model, x:Union[str, AnalyticsColumnInfo], y:Union[str, AnalyticsColumnInfo],
                      coldata:Dict[str, Dict], allcols: List[str], steps:int=20,
                      outputkey: str = 'Output') -> GraphData:
    """
    Creates a dataset from a 2d prediction on a ML model.

    Call from Grid to autogen params.

    Coldata should be formatted with keys 'min', 'max', 'mean'

    :param model: A ML model
    :param model: A ML model
    :param x: xaxis for graph data
    :param y: yaxis for graph data
    :param coldata: An dict of dicts accessed by col names with min, max, and mean values
    :param allcols: Ordered list of column names
    :param steps: Resolution to scan model with
    :param outputkey: Used to override default output name
    """
    if isinstance(x, AnalyticsColumnInfo):
        x = x.name
    if isinstance(y, AnalyticsColumnInfo):
        y = y.name

    assert x in coldata, "X must be in coldata"
    assert y in coldata, "Y must be in coldata"

    cols = []
    srow = []
    for name, item in coldata.items():
        if name not in [x, y]:
            cols.append(name)
        srow.append(item['mean'])

    srow = [srow] * (steps ** 2)
    preddata = pd.DataFrame(srow, columns=allcols)

    col = []
    for pos in range(0, steps):
        col.append(round(pos * (coldata[x]['max'] - coldata[x]['min']) / (steps - 1) + coldata[x]['min'], 6))
    col = col * steps
    preddata[x] = col

    col = []
    for pos in range(0, steps):
        col += [round(pos * (coldata[y]['max'] - coldata[y]['min']) / (steps - 1) + coldata[y]['min'], 6)] * steps
    preddata[y] = col

    predictions = model.predict(preddata)
    if outputkey in preddata.columns:
        warnings.warn(f"Output key '{outputkey}' was already in dataframe. This means that '{outputkey}' "
                      "was a key in your dataset and could result in data being overwritten. "
                      "You can pick a different key in the function call.")
    preddata[outputkey] = predictions
    return GraphData(preddata, GraphDataTypes.Grid, steps, x, y, outputkey=outputkey)
#endregion grid

#region animation
def predictionAnimation(model, x:Union[str, AnalyticsColumnInfo], y:Union[str, AnalyticsColumnInfo],
                        anim:Union[str, AnalyticsColumnInfo], data: pd.DataFrame, exclude:List[str] = None,
                        steps:int=20, outputkey: str = 'Output') -> GraphData:
    """
    Creates a dataset from a 2d prediction on a ML model. Wrapper function for PredictionGridRaw()
    that automatically handles column info generation.

    :param model: A ML model
    :param x: xaxis for graph data
    :param y: yaxis for graph data
    :param anim: Animation axis for graph data
    :param data: A pandas dataframe
    :param exclude: Values to be excluded from data, useful for output values
    :param steps: Resolution to scan model with
    :param outputkey: Used to override default output name
    """
    coldata, allcols = colinfo(data, exclude)
    return predictionAnimationRaw(model, x, y, anim, coldata, allcols, steps, outputkey)

def predictionAnimationRaw(model, x:Union[str, AnalyticsColumnInfo], y:Union[str, AnalyticsColumnInfo],
                           anim:Union[str, AnalyticsColumnInfo], coldata:Dict[str, Dict], allcols: List[str],
                           steps:int=20, outputkey: str = 'Output') -> GraphData:
    """
    Creates a dataset from a 2d prediction on a ML model.

    Call from PredictionAnimation to autogen params.

    Coldata should be formatted with keys 'name', 'min', 'max', 'mean'

    :param model: A ML model
    :param model: A ML model
    :param x: xaxis for graph data
    :param y: yaxis for graph data
    :param anim: Animation axis for graph data
    :param coldata: An dict of dicts accessed by col names with min, max, and mean values
    :param allcols: Ordered list of column names
    :param steps: Resolution to scan model with
    :param outputkey: Used to override default output name
    """

    if isinstance(x, AnalyticsColumnInfo):
        x = x.name
    if isinstance(y, AnalyticsColumnInfo):
        y = y.name
    if isinstance(anim, AnalyticsColumnInfo):
        anim = anim.name

    assert x in coldata, "X must be in coldata"
    assert y in coldata, "Y must be in coldata"
    assert anim in coldata, "Anim must be in coldata"

    cols = []
    srow = []
    for name, item in coldata.items():
        if name not in [x, y, anim]:
            cols.append(name)
        srow.append(item['mean'])

    srow = [srow] * (steps ** 3)
    preddata = pd.DataFrame(srow, columns=allcols)

    col = []
    for pos in range(0, steps):
         col.append(round(pos * (coldata[x]['max'] - coldata[x]['min']) / (steps - 1) + coldata[x]['min'], 6))
    col = col * (steps ** 2)
    preddata[x] = col

    col = []
    for pos in range(0, steps):
        col += [round(pos * (coldata[y]['max'] - coldata[y]['min']) / (steps - 1) + coldata[y]['min'], 6)] * steps
    col = col * steps
    preddata[y] = col

    col = []
    for pos in range(0, steps):
        col += [round(pos * (coldata[anim]['max'] - coldata[anim]['min']) / (steps - 1) + coldata[anim]['min'],6 )] * (steps ** 2)
    preddata[anim] = col

    predictions = model.predict(preddata)
    if outputkey in preddata.columns:
        warnings.warn(f"Output key '{outputkey}' was already in dataframe. This means that '{outputkey}' "
                      "was a key in your dataset and could result in data being overwritten. "
                      "You can pick a different key in the function call.")
    preddata[outputkey] = predictions
    return GraphData(preddata, GraphDataTypes.Animation, steps, x, y, anim, outputkey)

#endregion
