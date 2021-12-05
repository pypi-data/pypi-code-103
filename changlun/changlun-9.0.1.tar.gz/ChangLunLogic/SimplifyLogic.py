from ChangLunLogic.Model import *

def simplifyHistData(histData):
    if histData is None or len(histData) <= 2:
        return None
    simplifyData = []
    simplifyData.append(_createSimplifyDataFromHistData(histData,0))
    simplifyData[-1]['index'] = len(simplifyData) - 1
    for i in range(1,len(histData)):
        simplifyNextBar(simplifyData,histData,i)
    return simplifyData

def simplifyNextBar(simplifyData,histData,i):
    isBarContain = _getBarContainType(simplifyData[-1], histData[i])
    if isBarContain == BarContainType.none:
        newData = _createSimplifyDataFromHistData(histData, i)
        simplifyData.append(newData)
        simplifyData[-1]['index'] = len(simplifyData) - 1
        return

    direction = _getDirection(simplifyData)
    if isBarContain == BarContainType.left:
        if direction == Direction.down:
            simplifyData[-1]['high'] = histData[i]['high']
        else:
            simplifyData[-1]['low'] = histData[i]['low']
    else:
        if direction == Direction.down:
            simplifyData[-1]['low'] = histData[i]['low']
            simplifyData[-1]['orginIndex'] = i
            simplifyData[-1]['date'] = histData[i]['date']
        else:
            simplifyData[-1]['high'] = histData[i]['high']
            simplifyData[-1]['orginIndex'] = i
            simplifyData[-1]['date'] = histData[i]['date']

def _getDirection(simplifyData):
    if len(simplifyData) < 2:
        return Direction.down
    assert _getBarContainType(simplifyData[-2],simplifyData[-1]) == BarContainType.none
    if simplifyData[-1]['high'] > simplifyData[-2]['high']:
        return Direction.up
    return Direction.down

def _createSimplifyDataFromHistData(histData,index):
    simplifyBar = {}
    simplifyBar['high'] = histData[index]['high']
    simplifyBar['low'] = histData[index]['low']
    simplifyBar['date'] = histData[index]['date']
    simplifyBar['orginIndex'] = index
    return simplifyBar

def _getBarContainType(barLeft,barRigh):
    if barLeft['high'] >= barRigh['high'] and barLeft['low'] <= barRigh['low']:
        return BarContainType.left
    if barLeft['high'] <= barRigh['high'] and barLeft['low'] >= barRigh['low']:
        return BarContainType.right
    return BarContainType.none

