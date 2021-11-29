"""
Data Interface

A set of functions to add datapoints onto an ML response dataset.
"""

from MLVisualizationTools.backend import GraphData, colinfo
from typing import Optional
import pandas as pd

def getHashablePoint(point, graphData, coldata, outputkey, sizekey):
    """Get dictionary information for point clumping"""

    def roundScale(pval, colname, steps):
        minval = coldata[colname]['min']
        maxval = coldata[colname]['max']

        v = round((pval - minval) / ((maxval - minval) / steps)) #scale down to step pos
        return v, round(v * ((maxval - minval) / steps) + minval,6) #scale back to rounded true pos

    sep = ':'

    x, truex = roundScale(point[graphData.x], graphData.x, graphData.steps - 1)
    y, truey = roundScale(point[graphData.y], graphData.y, graphData.steps - 1)
    z, truez = roundScale(point[outputkey], outputkey, graphData.steps - 1)
    pdict = {graphData.x: truex, graphData.y: truey, graphData.outputkey: truez, sizekey: 1}

    hashstr = str(z) + sep + str(x) + sep + str(y)
    if graphData.anim is not None:
        anim, trueanim = roundScale(point[graphData.anim], graphData.anim, graphData.steps - 1)
        hashstr += sep + str(anim)
        pdict[graphData.anim] = trueanim
    return hashstr, pdict

def addClumpedData(graphData: GraphData, dataframe: pd.DataFrame, outputkey: str = 'Output',
                   sizekey: Optional[str] = None) -> GraphData:
    """
    Adds datapoints from dataframe to graphData. Point size is based on frequency of points at that location

    :param graphData: From an interface call
    :param dataframe: Dataframe of points to be added
    :param outputkey: Key in dataframe that represents output of model
    :param sizekey: Used for storing amount of datapoints in a group, must not be in df
    """
    if sizekey is not None:
        graphData.sizekey = sizekey
    graphData.check_size_key()

    if outputkey not in dataframe.columns:
        raise UserWarning(f"Output key '{outputkey}' was not in dataframe. You may need to override the default in the "
                          "function call.")

    coldata, _ = colinfo(dataframe)
    clumpedData = {}

    for _, point in dataframe.iterrows():
        hashstr, pdict = getHashablePoint(point, graphData, coldata, outputkey, graphData.sizekey)
        if hashstr in clumpedData:
            clumpedData[hashstr][graphData.sizekey] += 1
        else:
            clumpedData[hashstr] = pdict

    graphData.add_datavalues(pd.DataFrame.from_dict(clumpedData, orient='index'))
    return graphData

def getHashablePercentagePoint(point, graphData, coldata, outputkey):
    """Get dictionary information for point percentage clumping"""

    def roundScale(pval, colname, steps):
        minval = coldata[colname]['min']
        maxval = coldata[colname]['max']

        v = round((pval - minval) / ((maxval - minval) / steps)) #scale down to step pos
        return v, round(v * ((maxval - minval) / steps) + minval,6) #scale back to rounded true pos

    sep = ':'

    x, truex = roundScale(point[graphData.x], graphData.x, graphData.steps - 1)
    y, truey = roundScale(point[graphData.y], graphData.y, graphData.steps - 1)
    truez = point[outputkey]
    pdict = {graphData.x: truex, graphData.y: truey, graphData.outputkey: [truez]}

    hashstr = str(x) + sep + str(y)
    if graphData.anim is not None:
        anim, trueanim = roundScale(point[graphData.anim], graphData.anim, graphData.steps - 1)
        hashstr += sep + str(anim)
        pdict[graphData.anim] = trueanim
    return hashstr, pdict

def addPercentageData(graphData: GraphData, dataframe: pd.DataFrame, outputkey: str = 'Output',
                      sizekey: Optional[str] = None) -> GraphData:
    """
    Adds datapoints from dataframe to graphData. Point size is based on frequency of points at that location
    Point height is based on the average of point heights at that location

    :param graphData: From an interface call
    :param dataframe: Dataframe of points to be added
    :param outputkey: Key in dataframe that represents output of model
    :param sizekey: Used for storing amount of datapoints in a group, must not be in df
    """
    if sizekey is not None:
        graphData.sizekey = sizekey
    graphData.check_size_key()

    if outputkey not in dataframe.columns:
        raise UserWarning(f"Output key '{outputkey}' was not in dataframe. You may need to override the default in the "
                          "function call.")

    coldata, _ = colinfo(dataframe)
    clumpedData = {}

    for _, point in dataframe.iterrows():
        hashstr, pdict = getHashablePercentagePoint(point, graphData, coldata, outputkey)
        if hashstr in clumpedData:
            clumpedData[hashstr][graphData.outputkey].append(pdict[graphData.outputkey][0])
        else:
            clumpedData[hashstr] = pdict

    for key in clumpedData:
        l = len(clumpedData[key][graphData.outputkey])
        clumpedData[key][graphData.sizekey] = l
        clumpedData[key][graphData.outputkey] = sum(clumpedData[key][graphData.outputkey]) / l

    graphData.add_datavalues(pd.DataFrame.from_dict(clumpedData, orient='index'))
    return graphData

