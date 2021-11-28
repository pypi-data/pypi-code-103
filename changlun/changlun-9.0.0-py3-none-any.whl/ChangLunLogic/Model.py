#coding=utf-8

class CentrePosition:
    high = 'high'
    middle = 'middle'
    low = 'low'
    none = 'none'

class Direction:
    up = 1
    down = -1

class BarContainType:
    left = -1
    right = 1
    none = 0

class PartingType:
    up = 1
    down = -1
    none = 0

class PenType:
    up = 1
    down = -1

class DepartureType:
    up = 1
    down = -1
    none = 0

class CentreUpdateType:
    forwardBroken = 0
    backwardBroken = 1
    forwardMove = 2
    backwardMove = 3
    innerInclude = 4
    outerInclude = 5

class BuyPointsType:
    firstBuy = 'firstBuy'
    secondBuy = 'SecondBuy'
    thirdBuy = 'thirdBuy'
    secondThirdBuy = 'SecondThirdBuy'
    firstSell = 'firstSell'
    secondSell = 'secondSell'
    thirdSell = 'thirdSell'
    downDeparture = 'downDeparture'
    limitSell = 'limitSell'
    buySell = 'buySell'

    @staticmethod
    def getBuyPointSimple(tradeType):
        dic = {
            BuyPointsType.firstBuy : 1,
            BuyPointsType.secondBuy: 2,
            BuyPointsType.thirdBuy: 3,
            BuyPointsType.secondThirdBuy: 23,
            BuyPointsType.firstSell: 11,
            BuyPointsType.secondSell: 12,
            BuyPointsType.thirdSell: 13,
            BuyPointsType.downDeparture: 0,
            BuyPointsType.limitSell: 14,
            BuyPointsType.buySell : 8
        }
        return dic[tradeType]

    @staticmethod
    def getBuyPointDesc(tradeType):
        dic = {
            BuyPointsType.firstBuy : '一买',
            BuyPointsType.secondBuy: '二买',
            BuyPointsType.thirdBuy: '三买',
            BuyPointsType.secondThirdBuy: '二三买共振',
            BuyPointsType.firstSell: '一卖',
            BuyPointsType.secondSell: '二卖',
            BuyPointsType.thirdSell: '三卖',
            BuyPointsType.downDeparture: '盘整背驰',
            BuyPointsType.limitSell: '止损',
            BuyPointsType.buySell : '止盈'
        }
        return dic[tradeType]

    @staticmethod
    def isBuyPoints(tradeType):
        BuyTypeList = [BuyPointsType.firstBuy,BuyPointsType.secondBuy,BuyPointsType.thirdBuy,BuyPointsType.secondThirdBuy,BuyPointsType.downDeparture]
        if tradeType in BuyTypeList:
            return True
        return False

    @staticmethod
    def isSellPoints(tradeType):
        SellTypeList = [BuyPointsType.firstSell,BuyPointsType.secondSell,BuyPointsType.thirdSell,BuyPointsType.limitSell,BuyPointsType.buySell]
        if tradeType in SellTypeList:
            return True
        return False

class IndexType:
        partingIndex = 0
        penStartIndex = 1
        penEndIndex = 2
        segmentStartIndex = 3
        segmentEndIndex = 4
        centreStartIndex = 5
        centreEndIndex = 6
        trendStartIndex = 7
        trendEndIndex = 8
        histDataIndex = 9

class BuyPoint:
    def __init__(self):
        self.index = None
        self.value = None
        self.type = None
        self.date = None

class Parting:
    def __init__(self):
        self.partingType = None
        self.partingValue = None
        self.dateTime = None
        self.barIndex = -1
        self.leftBar = None
        self.middleBar = None
        self.rightBar = None

class Pen:
    def __init__(self):
        self.startDate = None
        self.endDate = None
        self.startIndex = None
        self.endIndex = None
        self.startValue = None
        self.endValue = None
        self.isValid = True

    def setValue(self,startDate,startValue,startIndex,endDate,endValue,endIndex,isValid=True):
        self.startDate = startDate
        self.startValue = startValue
        self.startIndex = startIndex
        self.endDate = endDate
        self.endValue = endValue
        self.endIndex = endIndex
        self.isValid = isValid

    def getPenType(self):
        if self.startValue > self.endValue:
            return PenType.down
        else:
            return PenType.up

    @staticmethod
    def createPenFromPartingList(partingList,startIndex,endIndex):
        startParting = partingList[startIndex]
        endParting = partingList[endIndex]
        assert isinstance(startParting,Parting)
        assert isinstance(endParting,Parting)
        pen = Pen()
        pen.startIndex = startParting.barIndex
        pen.endIndex = endParting.barIndex
        pen.startDate = startParting.dateTime
        pen.endDate = endParting.dateTime
        pen.startValue = startParting.partingValue
        pen.endValue = endParting.partingValue
        return pen

class Centre:
    def __init__(self):
        self.startIndex = None
        self.endIndex = None
        self.startDate = None
        self.endDate = None
        self.low = None
        self.high = None

    def setValue(self,startIndex,endIndex,startDate,endDate,low,high):
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.startDate = startDate
        self.endDate = endDate
        self.low = low
        self.high = high
