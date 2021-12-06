from ChangLunLogic.Model import *
import ChangLunLogic.CommonUtils as CommonUtils

class SegmentsCreateLogic:
    def __init__(self,penList):
        self.isBrokenBeginPoint = False
        self.penList = penList
        self.startIndex = 0
        self.startValue = 0.0
        self.hasSegment = False
        self.segmentList = []
        self.segmentType = None
        self.centre = {}
        self.centerNum = 0
        self.lastCenterPenNum = 0
        self.extremeIndex = 0
        self.extremePoint = 0.0
        self.isEnd = False
        self._createSegment()
        self.fixLastSegment()
        self.centreList = []

    def fixLastSegment(self):
        if len(self.segmentList) == 0:
            return
        lastSegment = self.segmentList[-1]
        if lastSegment['endPenIndex'] == len(self.penList):
            return
        if lastSegment['type'] == PenType.up and self.penList[-1]['endValue'] >= lastSegment['endValue'] \
            or lastSegment['type'] == PenType.down and self.penList[-1]['endValue'] <= lastSegment['endValue']:
            lastSegment['endValue'] = self.penList[-1]['endValue']
            lastSegment['endDate'] = self.penList[-1]['endDate']
            lastSegment['endOrginIndex'] = self.penList[-1]['endOrginIndex']
            lastSegment['endSimplifyIndex'] = self.penList[-1]['endSimplifyIndex']
            lastSegment['endPenIndex'] = len(self.penList)

    def _getNewCentreFromPen(self,pen):
        newCentre = {}
        newCentre['high'] = max(pen['startValue'],pen['endValue'])
        newCentre['low'] = min(pen['startValue'],pen['endValue'])
        return newCentre

    def _getNewCentreType(self,centre,newCentre):
        if newCentre['high'] <= centre['high'] and newCentre['low'] >= centre['low']:
            return CentreUpdateType.innerInclude
        if newCentre['high'] >= centre['high'] and newCentre['low'] <= centre['low']:
            return CentreUpdateType.outerInclude
        isBroken = newCentre['high'] <= centre['low'] or newCentre['low'] >= centre['high']
        if (newCentre['high'] > centre['high'] and self.segmentType == PenType.up) or (newCentre['low'] < centre['low'] and self.segmentType == PenType.down):
            if isBroken:
                return CentreUpdateType.forwardBroken
            else:
                return CentreUpdateType.forwardMove
        else:
            if isBroken:
                return CentreUpdateType.backwardBroken
            else:
                return CentreUpdateType.backwardMove

    def _createSegment(self):
        if self.penList is None:
            return
        if self.isEnd:
            return
        if len(self.penList[self.startIndex:]) < 3:
            return
        self._initData()
        if self.isBrokenBeginPoint:
            self._createSegmentFromPens(self.startIndex, self.extremeIndex)
            self.startIndex = self.extremeIndex + 1
            self._createSegment()
            return
        nextPenIndex = self.startIndex + 3
        while nextPenIndex < len(self.penList):
            nextPen = self.penList[nextPenIndex]
            newCentre = self._getNewCentreFromPen(nextPen)
            centreUpdateType = self._getNewCentreType(self.centre,newCentre)
            if centreUpdateType == CentreUpdateType.forwardBroken or centreUpdateType == CentreUpdateType.forwardMove:
                if centreUpdateType == CentreUpdateType.forwardBroken:
                    self.centerNum += 1
                    self.lastCenterPenNum = 1
                else:
                    self.lastCenterPenNum += 1
                self._updateCentre(nextPen)
                self.extremeIndex = nextPenIndex - 1
                self.extremePoint = self.penList[nextPenIndex-1]['endValue']
                self.hasSegment = True
                nextPenIndex += 2
                continue
            if centreUpdateType == CentreUpdateType.outerInclude:
                if (self.segmentType == PenType.up and nextPen['endValue'] < self.startValue) or (self.segmentType == PenType.down and nextPen['endValue'] > self.startValue):
                    self.extremeIndex = nextPenIndex - 1
                    self._createSegmentFromPens(self.startIndex,self.extremeIndex)
                    self.startIndex = self.extremeIndex + 1
                    self._createSegment()
                    return
                else:
                    self.lastCenterPenNum += 1
                    self.updateCentrePenBroken(nextPen)
                    self.extremeIndex = nextPenIndex - 1
                    self.extremePoint = self.penList[nextPenIndex - 1]['endValue']
                    nextPenIndex += 2
                    continue
            if centreUpdateType == CentreUpdateType.innerInclude:
                self.lastCenterPenNum += 1
                nextPenIndex += 2
                continue
            if centreUpdateType == CentreUpdateType.backwardMove:
                if self.hasSegment:
                    if not self.centre['isPenBroken']:
                        self._createSegmentFromPens(self.startIndex,self.extremeIndex)
                        self.startIndex = self.extremeIndex + 1
                        self._createSegment()
                        return
                    else:
                        if ( self.segmentType == PenType.up and nextPen['endValue'] < self.centre['orginLow'] ) \
                                or (self.segmentType == PenType.down and nextPen['startValue'] > self.centre['orginHigh']):
                            self._createSegmentFromPens(self.startIndex, self.extremeIndex)
                            self.startIndex = self.extremeIndex + 1
                            self._createSegment()
                            return
                        else:
                            nextPenIndex += 2
                            continue
                else:
                    if self._isPenBrokenStartPoint(nextPen):
                        self._createSegmentFromPens(self.startIndex,self.extremeIndex)
                        self.startIndex = self.extremeIndex + 1
                        self._createSegment()
                        return
                    else:
                        nextPenIndex += 2
                        continue
            if centreUpdateType == CentreUpdateType.backwardBroken:
                self._createSegmentFromPens(self.startIndex, self.extremeIndex)
                self.startIndex = self.extremeIndex + 1
                self._createSegment()
                return
        self._createSegmentFromPens(self.startIndex,self.extremeIndex)
        self.isEnd = True

    def _initData(self):
        self.isBrokenBeginPoint = False
        self.segmentType = self.penList[self.startIndex]['type']
        self.startValue = self.penList[self.startIndex]['startValue']
        if (self.segmentType == PenType.up and self.penList[self.startIndex+2]['endValue'] > self.penList[self.startIndex]['endValue'])\
                or (self.segmentType == PenType.down and self.penList[self.startIndex+2]['endValue'] < self.penList[self.startIndex]['endValue']):
            self.hasSegment = True
            self.extremeIndex = self.startIndex + 2
            self.extremePoint = self.penList[self.startIndex+2]['endValue']
        else:
            self.hasSegment = False
            self.extremeIndex = self.startIndex
            self.extremePoint = self.penList[self.startIndex]['endValue']
            if self.segmentType == PenType.up and self.penList[self.startIndex+1]['endValue'] < self.penList[self.startIndex]['startValue']:
                self.isBrokenBeginPoint = True
            if self.segmentType == PenType.down and self.penList[self.startIndex+1]['endValue'] > self.penList[self.startIndex]['startValue']:
                self.isBrokenBeginPoint = True

        self._updateCentre(self.penList[self.startIndex+1])
        self.centerNum = 1
        self.lastCenterPenNum = 1

    def _updateCenterManual(self,startIndex,high,low):
        self.centre['high'] = high
        self.centre['low'] = low
        self.centre['startIndex'] = startIndex

    def updateCentrePenBroken(self,nextPen):
        if nextPen['type'] == PenType.down:
            self.centre['high'] = nextPen['startValue']
            self.centre['startIndex'] = nextPen['index']
            self.centre['isPenBroken'] = True
            self.centre['orginLow'] = nextPen['endValue']
            self.centre['orginHigh'] = nextPen['startValue']
        else:
            self.centre['low'] = nextPen['startValue']
            self.centre['startIndex'] = nextPen['index']
            self.centre['isPenBroken'] = True
            self.centre['orginLow'] = nextPen['startValue']
            self.centre['orginHigh'] = nextPen['endValue']

    def _updateCentre(self,nextPen):
        if nextPen['type'] == PenType.down:
            self.centre['high'] = nextPen['startValue']
            self.centre['low'] = nextPen['endValue']
            self.centre['startIndex'] = nextPen['index']
            self.centre['isPenBroken'] = False
            self.centre['orginLow'] = nextPen['endValue']
            self.centre['orginHigh'] = nextPen['startValue']
        else:
            self.centre['high'] = nextPen['endValue']
            self.centre['low'] = nextPen['startValue']
            self.centre['startIndex'] = nextPen['index']
            self.centre['isPenBroken'] = False
            self.centre['orginLow'] = nextPen['startValue']
            self.centre['orginHigh'] = nextPen['endValue']

    def _updateExtrePoints(self,nextPen):
        if nextPen['type'] == PenType.down:
            if nextPen['startValue'] > self.extremePoint:
                self.extremePoint = nextPen['startValue']
                self.extremeIndex = nextPen['index']
            if nextPen['endValue'] < self.revesreExtrePoint:
                self.revesreExtrePoint = nextPen['endValue']
                self.revesreExtreIndex = nextPen['index']
        else:
            if nextPen['startValue'] < self.extremePoint:
                self.extremePoint = nextPen['startValue']
                self.extremeIndex = nextPen['index']
            if nextPen['endValue'] > self.revesreExtrePoint:
                self.revesreExtrePoint = nextPen['endValue']
                self.revesreExtreIndex = nextPen['index']

    def _isPenBrokenStartPoint(self,nextPen):
        startValue = self.penList[self.startIndex]['startValue']
        if self.segmentType == PenType.down and nextPen['endValue'] > startValue:
            return True
        if self.segmentType == PenType.up and nextPen['endValue'] < startValue:
            return True
        return False

    def _isCentreAndPenOverlap(self,center,nextPen):
        minPen = min(nextPen['startValue'],nextPen['endValue'])
        maxPen = max(nextPen['startValue'],nextPen['endValue'])
        if center['low'] >= maxPen or center['high'] <= minPen:
            return False
        return True

    def _isNewCentreForward(self,nextPen):
        if nextPen['type'] == PenType.up and nextPen['endValue'] < self.centre['low']:
            return True
        if nextPen['type'] == PenType.down and nextPen['endValue'] > self.centre['high']:
            return True
        return False

    def _createForwardCentreSegments(self,nextPenType):
        assert self.centrePenCount > 3
        extremePenIndex = self.extremeIndex
        if self.extremeIndex > self.revesreExtreIndex:
            if nextPenType == PenType.down:
                extremePen = max(self.penList[self.startIndex + 1:self.revesreExtreIndex + 1],key = lambda x: x['startValue'])
            else:
                extremePen = min(self.penList[self.startIndex + 1:self.revesreExtreIndex + 1],key = lambda x: x['startValue'])
            extremePenIndex = extremePen['index']
        self._createSegmentFromPens(self.startIndex,extremePenIndex - 1)
        self._createSegmentFromPens(extremePenIndex,self.revesreExtreIndex)
        self._setNextStart(self.revesreExtreIndex+1)

    def _resetCentrePenCount(self):
        self.centrePenCount = 0

    def _setNextStart(self,endIndex):
        self.startIndex = endIndex

    def _createSegmentFromPens(self,startIndex, endIndex):
        segment = {}
        segment['startValue'] = self.penList[startIndex]['startValue']
        segment['startDate'] = self.penList[startIndex]['startDate']
        segment['startOrginIndex'] = self.penList[startIndex]['startOrginIndex']
        segment['startSimplifyIndex'] = self.penList[startIndex]['startSimplifyIndex']
        segment['startPenIndex'] = startIndex
        segment['endValue'] = self.penList[endIndex]['endValue']
        segment['endDate'] = self.penList[endIndex]['endDate']
        segment['endOrginIndex'] = self.penList[endIndex]['endOrginIndex']
        segment['endSimplifyIndex'] = self.penList[endIndex]['endSimplifyIndex']
        segment['endPenIndex'] = endIndex
        segment['type'] = self.penList[startIndex]['type']
        if endIndex - startIndex < 2:
            segment['isValid'] = False
        else:
            segment['isValid'] = True
        segment['centerNum'] = self.centerNum
        segment['lastCenterPenNum'] = self.lastCenterPenNum
        self.segmentList.append(segment)

def createSegmentList(penList):
    segmentLogic = SegmentsCreateLogic(penList)
    segmentList = CommonUtils.addIndex(segmentLogic.segmentList)
    return segmentList




