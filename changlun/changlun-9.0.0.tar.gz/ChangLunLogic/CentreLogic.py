__author__ = 'shenli'
import ChangLunLogic.CommonUtils as CommonUtils

def createCentreList(segmentList,penList):
    if segmentList is None:
        return None
    centreList = []
    for i in range(0,len(segmentList)):
        startIndex,endIndex = _getSegmentStartEndIndex(segmentList,i,penList)
        tempList = _createCentreListFromPens(penList,startIndex,endIndex,i)
        centreList.extend(tempList)
    centreList = CommonUtils.addIndex(centreList)
    return centreList

def _createCentreListFromPens(penList,startIndex,endIndex,segmentIndex):
    if startIndex == endIndex:
        return []
    centreStart = startIndex + 1
    centreEnd = centreStart + 2
    centreList = []
    while centreEnd < endIndex:
        if _isPenOverlap(penList[centreStart],penList[centreEnd]):
            centreEnd += 2
            continue
        centre = _createCentre(penList,centreStart,centreEnd-2,segmentIndex)
        centreList.append(centre)
        centreStart = centreEnd
        centreEnd = centreStart + 2
    if centreEnd >= endIndex and centreEnd - 2 >= centreStart:
        centre = _createCentre(penList,centreStart,centreEnd-2,segmentIndex)
        centreList.append(centre)
    return centreList

def _createCentre(penList,centreStart,centreEnd,segmentIndex):
    centre = {}
    centre['startDate'] = penList[centreStart]['startDate']
    centre['endDate'] = penList[centreEnd]['endDate']
    centre['startOrginIndex'] = penList[centreStart]['startOrginIndex']
    centre['endOrginIndex'] = penList[centreEnd]['endOrginIndex']
    centre['startPenIndex'] = centreStart
    centre['endPenIndex'] = centreEnd
    centre['segmentIndex'] = segmentIndex
    centre['low'] = min(penList[centreStart]['startValue'],penList[centreStart]['endValue'])
    centre['high'] = max(penList[centreStart]['startValue'],penList[centreStart]['endValue'])
    maxStart = max(penList[centreStart:centreEnd+1],key = lambda x:x['startValue'])['startValue']
    minStart = min(penList[centreStart:centreEnd+1],key = lambda x:x['startValue'])['startValue']
    maxEnd = max(penList[centreStart:centreEnd+1],key = lambda x:x['endValue'])['endValue']
    minEnd = min(penList[centreStart:centreEnd+1],key = lambda x:x['endValue'])['endValue']
    centre['extremeHigh'] = max(maxStart,maxEnd)
    centre['extremeLow'] = min(minStart,minEnd)
    return centre


def _isPenOverlap(pen1,pen2):
    min1 = min(pen1['startValue'],pen1['endValue'])
    max1 = max(pen1['startValue'],pen1['endValue'])
    min2 = min(pen2['startValue'],pen2['endValue'])
    max2 = max(pen2['startValue'],pen2['endValue'])
    if min1 > max2 or max1 < min2:
        return False
    return True

def _getSegmentStartEndIndex(segmentList,index,penList):
    startIndex = segmentList[index]['startPenIndex']
    endIndex = segmentList[index]['endPenIndex']
    #if index == len(segmentList) - 1:
        #endIndex = len(penList) - 1
    return (startIndex,endIndex)
