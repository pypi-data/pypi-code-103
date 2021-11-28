from ChangLunLogic.Model import *

def getPartingList(simplifyData):
    if simplifyData is None or len(simplifyData) < 3:
        return None
    partingList = []
    for i in range(0,len(simplifyData)-2):
        appenParting(simplifyData,i,partingList)
    return partingList

def appenParting(simplifyData,i,partingList):
    window = 3
    partingType = _getPartingType(simplifyData[i:i + window])
    if partingType == PartingType.none:
        return
    orginIndex = simplifyData[i + 1]['orginIndex']
    date = simplifyData[i + 1]['date']
    if partingType == PartingType.down:
        value = simplifyData[i + 1]['low']
    else:
        value = simplifyData[i + 1]['high']
    extremePoints = _getPartingExtremePoints(simplifyData[i:i + window])
    parting = _createParting(i + 1, orginIndex, date, value, partingType, extremePoints)
    partingList.append(parting)
    partingList[-1]['index'] = len(partingList) - 1

def _getPartingExtremePoints(windowData):
    '''
    minValue = min(windowData,key = lambda x:x['low'])
    maxValue = max(windowData,key = lambda x:x['high'])
    return (minValue['low'],maxValue['high'])
    '''

    leftHigh = windowData[0]['high']
    leftLow = windowData[0]['low']
    midHigh = windowData[1]['high']
    midLow = windowData[1]['low']
    rightHigh = windowData[2]['high']
    rightLow = windowData[2]['low']
    return (leftLow,leftHigh,midLow,midHigh,rightLow,rightHigh)


def _createParting(simplifyIndex,orginIndex,date,value,type,extremePoints):
    parting = {}
    parting['orginIndex'] = orginIndex
    parting['simplifyIndex'] = simplifyIndex
    parting['date'] = date
    parting['value'] = value
    parting['type'] = type
    parting['leftLow'] = extremePoints[0]
    parting['leftHigh'] = extremePoints[1]
    parting['midLow'] = extremePoints[2]
    parting['midHigh'] = extremePoints[3]
    parting['rightLow'] = extremePoints[4]
    parting['rightHigh'] = extremePoints[5]
    return parting

def _getPartingType(windowData):
    assert len(windowData) == 3
    if windowData[1]['high'] > windowData[0]['high'] and windowData[1]['high'] > windowData[2]['high']:
        return PartingType.up
    if windowData[1]['low'] < windowData[0]['low'] and windowData[1]['low'] < windowData[2]['low']:
        return PartingType.down
    return PartingType.none
