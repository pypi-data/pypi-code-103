"""
Model Analytics

A set of functions to anaylze how a ML model responds to different inputs.
All functions return an AnalyticsResult object that contains data about different columns.

Analytics functions can be called directly with a pandas dataframe, or indirectly through
the raw alternative, which takes a colinfo object.
"""


from MLVisualizationTools.backend import colinfo
from typing import List, Dict
import copy
import pandas as pd

#Functions for retrieving data about ml model structure

#TODO - nonlinear

class AnalyticsColumnInfo:
    """Wrapper class for holding col info"""
    def __init__(self, name: str, variance: float):
        self.name = name
        self.variance = variance

    def __lt__(self, other):
        return self.variance < other.variance

    def __repr__(self):
        return "Col with name: " + self.name + " and variance " + str(self.variance)

class AnalyticsResult:
    """Wrapper class for holding and processing col info"""
    def __init__(self):
        self.cols: List[AnalyticsColumnInfo] = []

    def append(self, name: str, variance: float):
        self.cols.append(AnalyticsColumnInfo(name, variance))

    def maxVariance(self):
        """Return a list of cols, ordered by maximum variance"""
        cols = copy.copy(self.cols)
        cols.sort(reverse=True)
        return cols

def analyzeModel(model, data: pd.DataFrame, exclude: List[str] = None, steps:int=20) -> AnalyticsResult:
    """
    Performs 1d analysis on an ML model by calling predict(). Wrapper function for analyzeModelRaw()
    that automatically handles column info generation.

    :param model: A ML model
    :param data: A pandas dataframe
    :param exclude: Values to be excluded from data, useful for output values
    :param steps: Resolution to scan model with
    """
    coldata, allcols = colinfo(data, exclude)
    return analyzeModelRaw(model, coldata, allcols, steps)

def analyzeModelRaw(model, coldata: Dict[str, Dict], allcols: List[str], steps:int=20) -> AnalyticsResult:
    """
    Performs 1d analysis on a ML model by calling predict(). Returns a class with lots of info for graphing.
    Call from anaylyzeModel to autogen params.

    Coldata should be formatted with keys 'name', 'min', 'max', 'mean'

    :param model: A ML model
    :param coldata: An dict of dicts accessed by col names with min, max, and mean values
    :param allcols: Ordered list of column names
    :param steps: Resolution to scan model with
    """
    AR = AnalyticsResult()

    predrow = []
    for name, item in coldata.items():
        predrow.append(item['mean'])
    predrow = [predrow] * (steps * len(coldata))
    preddata = pd.DataFrame(predrow, columns=allcols)

    currentpos = 0
    for name, item in coldata.items():
        for i in range(0, steps):
            preddata[name][i + currentpos] = i * (item['max'] - item['min'])/(steps-1) + item['min']
        currentpos += steps

    predictions = model.predict(preddata)

    currentpos = 0
    for name in coldata:
        values = predictions[currentpos:currentpos + steps]
        currentpos += steps
        AR.append(name, values.max() - values.min())
    return AR