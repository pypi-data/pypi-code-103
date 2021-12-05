import ChangLunLogic.SimplifyLogic as SimplifyLogic
import ChangLunLogic.PartingLogic as PartingLogic
import ChangLunLogic.PenLogic as PenLogic
from ChangLunLogic.Model import *

def isPenChange(penList,histData):
    beforePen = penList[0]
    lastPen = penList[-1]
    startOrginIndex = beforePen['startOrginIndex']
    tempData = histData[startOrginIndex:]
    simpleData = SimplifyLogic.simplifyHistData(tempData)
    lastPartingType = PartingLogic._getPartingType(simpleData[-3:])
    if lastPartingType == PartingType.none:
        return False
    partingList = PartingLogic.getPartingList(simpleData)
    lastPenParting = None
    for parting in partingList:
        if parting['date'] == lastPen['endDate']:
            lastPenParting = parting
            break
    if lastPenParting is None:
        return False
    if PenLogic._isPenExist(lastPenParting,partingList[-1]) or PenLogic._isSameTypeAndMoreHigherOrLower(lastPenParting,partingList[-1]):
        return True
    else:
        return False

