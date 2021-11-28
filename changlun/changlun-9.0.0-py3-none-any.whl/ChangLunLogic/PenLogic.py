from ChangLunLogic.Model import *
import ChangLunLogic.CommonUtils as CommonUtils

def createPenList(partingList):
    if partingList is None:
        return None
    startIndex = _getStartIndex(partingList)
    lastIndex1 = startIndex
    lastIndex2 = None
    penList = []
    for i in range(startIndex + 1, len(partingList)):
        if _isPenExist(partingList[lastIndex1],partingList[i]):
            pen = _createPen(lastIndex1,i,partingList)
            penList.append(pen)
            lastIndex2 = lastIndex1
            lastIndex1 = i
            continue
        if len(penList) == 0:
            continue
        if _isSameTypeAndMoreHigherOrLower(partingList[lastIndex1],partingList[i]):
            pen = _createPen(lastIndex2,i,partingList)
            penList.pop(-1)
            penList.append(pen)
            lastIndex1 = i
            continue
        '''
        if len(penList) > 1 and _isSameTypeAndMoreHigherOrLower(partingList[lastIndex2],partingList[i]):
            penList.pop(-1)
            tempIndex = penList[-1]['startPartingIndex']
            pen = _createPen(tempIndex,i,partingList)
            penList.pop(-1)
            penList.append(pen)
            lastIndex2 = tempIndex
            lastIndex1 = i
        '''
    penList = CommonUtils.addIndex(penList)
    return penList

def _isSameTypeAndMoreHigherOrLower(parting1,parting2):
    if parting1['type'] != parting2['type']:
        return False
    if parting1['type'] == PartingType.up and parting2['value'] > parting1['value']:
            return True
    if parting1['type'] == PartingType.down and parting2['value'] < parting1['value']:
            return True
    return False

def _createPen(index1,index2,partingList):
    parting1 = partingList[index1]
    parting2 = partingList[index2]
    type = PenType.up
    if parting1['type'] == PartingType.up:
        type = PenType.down
    pen = {}
    pen['type'] = type
    pen['startDate'] = parting1['date']
    pen['endDate'] = parting2['date']
    pen['startValue'] = parting1['value']
    pen['endValue'] = parting2['value']
    pen['startSimplifyIndex'] = parting1['simplifyIndex']
    pen['endSimplifyIndex'] = parting2['simplifyIndex']
    pen['startOrginIndex'] = parting1['orginIndex']
    pen['endOrginIndex'] = parting2['orginIndex']
    pen['startPartingIndex'] = index1
    pen['endPartingIndex'] = index2
    return pen

def _isPenExist(parting1,parting2):
    if parting1['type'] == parting2['type']:
        return False
    type = getPartingCrossType(parting1,parting2)
    if type == 'leftContain' or type == 'rightContain':
        if parting2['orginIndex'] - parting1['orginIndex'] < 4:
            return False
        if parting1['type'] == PartingType.down and parting2['midLow'] > parting1['rightHigh']:
            return True
        if parting1['type'] == PartingType.up and parting2['midHigh'] < parting1['rightLow']:
            return True
    if type == 'upBroken' and parting1['type'] == PartingType.down and parting2['orginIndex'] - parting1['orginIndex'] >= 3:
        return True
    if type == 'downBroken' and parting1['type'] == PartingType.up and parting2['orginIndex'] - parting1['orginIndex'] >= 3:
        return True
    if type == 'upCross' and parting1['type'] == PartingType.down and parting2['orginIndex'] - parting1['orginIndex'] >= 4:
        return True
    if type == 'downCross' and parting1['type'] == PartingType.up and parting2['orginIndex'] - parting1['orginIndex'] >= 4:
        return True
    return False

def getPartingMinMax(parting):
    minValue = min(parting['leftLow'],parting['midLow'],parting['rightLow'])
    maxValue = max(parting['leftHigh'],parting['midHigh'],parting['rightHigh'])
    return (minValue,maxValue)

def getPartingCrossType(parting1,parting2):
    min1,max1 = getPartingMinMax(parting1)
    min2,max2 = getPartingMinMax(parting2)
    if min1 <= min2 and max1 >= max2 :
        return 'leftContain'
    if min2 <= min1 and max2 >= max1 :
        return 'rightContain'
    if min2 > max1:
        return 'upBroken'
    if max2 < min1:
        return 'downBroken'
    if max2 > max1:
        return 'upCross'
    if min2 < min1:
        return 'downCross'

def _getStartIndex(partingList):
    if partingList is None or len(partingList) == 0:
        return 0
    maxValue = 0
    maxIndex = 0
    minValue = 9999
    minIndex = 0
    for i in range(0,len(partingList)):
        partingType = partingList[i]['type']
        if partingType == PartingType.up and partingList[i]['value'] > maxValue:
            maxValue = partingList[i]['value']
            maxIndex = i
        if partingType == PartingType.down and partingList[i]['value'] < minValue:
            minValue = partingList[i]['value']
            minIndex = i
    startIndex = min(minIndex,maxIndex)
    startParting = partingList[startIndex]
    if startParting['orginIndex'] >= 250 and startIndex > 0:
        return _getStartIndex(partingList[0:startIndex])
    else:
        return startIndex

