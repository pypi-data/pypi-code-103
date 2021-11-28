from ChangLunLogic.Model import *
import UtilTools.DateUtils as DateUtils
import UtilTools.FrequencyUtils as FreqUtils

def getThirtyLevelBuyPoint(segmentDic,endDate,rootFreq = '30'):
    superFreq = FreqUtils.getSuperFreq(rootFreq)
    subFreq = FreqUtils.getSubFreq(rootFreq)
    subSegment = segmentDic[subFreq]
    childFreq = FreqUtils.getSubFreq(subFreq)
    childSegment = None
    if childFreq is not None:
        childSegment = segmentDic[childFreq]
    superSegment = segmentDic[superFreq]
    rootSegment = segmentDic[rootFreq]
    if rootSegment is None or rootSegment[-1]['type'] == PenType.up:
        return None

    isLastRootSegmentValid = isLastSegmentValid(rootSegment[-1],subSegment)
    lastSubSegment = subSegment[rootSegment[-1]['endPenIndex'] - 1]
    isLastSubSegmentValid = isLastSegmentValid(lastSubSegment,childSegment)
    if childFreq is None and not isLastRootSegmentValid:
        return None
    if not isLastRootSegmentValid and not isLastSubSegmentValid:
        return None
    lastSegmentEndDateStr = DateUtils.convertTimestampToStr(segmentDic[rootFreq][-1]['endDate'])
    if lastSegmentEndDateStr[0:10] != endDate[0:10]:
        return None
    if superSegment is None or len(superSegment) == 0:
        return createBuyPointFromSegment(rootSegment[-1],BuyPointsType.downDeparture,rootFreq)
    if superSegment[-1]['type'] == PenType.down:
        if isSegmentValid(superSegment[-1]):
            if superSegment[-1]['endDate'] == rootSegment[-1]['endDate']:
                return createBuyPointFromSegment(rootSegment[-1],BuyPointsType.firstBuy,rootFreq)
            else:
                if len(rootSegment) - superSegment[-1]['endPenIndex'] == 3:
                    return createBuyPointFromSegment(rootSegment[-1],BuyPointsType.secondBuy,rootFreq)
                else:
                    startPenIndex = superSegment[-1]['endPenIndex'] + 1
                    if isThirdBuy(rootSegment[startPenIndex:]):
                        return createBuyPointFromSegment(rootSegment[-1],BuyPointsType.thirdBuy,rootFreq)
                    else:
                        return createBuyPointFromSegment(rootSegment[-1],BuyPointsType.downDeparture,rootFreq)
        else:
            startPenIndex = superSegment[-1]['endPenIndex'] + 1
            if len(rootSegment[startPenIndex:]) > 3 and isThirdBuy(rootSegment[startPenIndex:]):
                return createBuyPointFromSegment(rootSegment[-1],BuyPointsType.thirdBuy,rootFreq)
            else:
                return createBuyPointFromSegment(rootSegment[-1],BuyPointsType.downDeparture,rootFreq)
    else:
        startPenIndex = superSegment[-1]['startPenIndex']
        if isThirdBuy(rootSegment[startPenIndex:]):
            return createBuyPointFromSegment(rootSegment[-1],BuyPointsType.thirdBuy,rootFreq)
        else:
            return createBuyPointFromSegment(rootSegment[-1],BuyPointsType.downDeparture,rootFreq)
    return None

def isLastSegmentValid(segment,subSegment):
    if subSegment is None:
        return False
    startIndex = segment['startPenIndex']
    endIndex = segment['endPenIndex']
    if endIndex - startIndex < 2:
        return False
    nextPenIndex = startIndex + 1
    center = getCenterFromPen(subSegment[nextPenIndex])
    nextPenIndex += 2
    while nextPenIndex < endIndex:
        newCenter = getCenterFromPen(subSegment[nextPenIndex])
        if newCenter['high'] > segment['startValue'] or newCenter['low'] < segment['endValue']:
            return False
        centerType = getNewCentreType(center,newCenter)
        if centerType in [CentreUpdateType.outerInclude, CentreUpdateType.forwardMove, CentreUpdateType.backwardMove,CentreUpdateType.innerInclude]:
            return True
        elif centerType == CentreUpdateType.backwardBroken:
            return False
        else:
            center = newCenter
            nextPenIndex += 2
    return False

def isThirdBuy(segmentList):
    if len(segmentList) < 4:
        return False
    nextSegmentIndex = 1
    center = getCenterFromPen(segmentList[nextSegmentIndex])
    nextSegmentIndex += 2
    while nextSegmentIndex < len(segmentList) - 1:
        newCenter = getCenterFromPen(segmentList[nextSegmentIndex])
        centerType = getNewCentreType(center,newCenter)
        if centerType in [CentreUpdateType.outerInclude,CentreUpdateType.forwardMove,CentreUpdateType.forwardBroken]:
            center = newCenter
        nextSegmentIndex += 2
    if segmentList[-1]['endValue'] > center['high']:
        return True
    return False

def getCenterFromPen(nextPen):
    center = {}
    if nextPen['type'] == PenType.down:
        center['high'] = nextPen['startValue']
        center['low'] = nextPen['endValue']
    else:
        center['high'] = nextPen['endValue']
        center['low'] = nextPen['startValue']
    return center


def getNewCentreType(centre, newCentre):
    if newCentre['high'] <= centre['high'] and newCentre['low'] >= centre['low']:
        return CentreUpdateType.innerInclude
    if newCentre['high'] >= centre['high'] and newCentre['low'] <= centre['low']:
        return CentreUpdateType.outerInclude
    isBroken = newCentre['high'] <= centre['low'] or newCentre['low'] >= centre['high']
    if newCentre['high'] > centre['high']:
        if isBroken:
            return CentreUpdateType.forwardBroken
        else:
            return CentreUpdateType.forwardMove
    else:
        if isBroken:
            return CentreUpdateType.backwardBroken
        else:
            return CentreUpdateType.backwardMove


def createBuyPointFromSegment(segment,buyType,level):
    buyPoint = BuyPoint()
    buyPoint.date = segment['endDate']
    buyPoint.index = segment['endOrginIndex']
    buyPoint.value = segment['endValue']
    buyPoint.type = buyType
    buyPoint.level = level
    return buyPoint

def isSegmentValid(segment):
    return segment['isValid']

