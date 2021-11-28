__author__ = 'shenli'
import UtilTools.DateUtils as DateUtils
import ChangLunLogic.SimplifyLogic as SimplifyLogic
import ChangLunLogic.PartingLogic as PartingLogic
import ChangLunLogic.PenLogic as PenLogic
import ChangLunLogic.SegmentLogic as SegmentLogic
import ChangLunLogic.CentreLogic as CentreLogic
import ChangLunLogic.BuyPointLogic as BuyPointLogic
import UtilTools.FrequencyUtils as FreqUtils
from ChangLunLogic.Model import *
import pandas as pd

class ChangLun:
    def __init__(self, stockDf, baseFreq,rootFreq):
        self.baseFreq = baseFreq
        self.rootFreq = rootFreq
        self.buyPoints = {}
        self.histData = self.convertDfToHistData(stockDf)
        self.lastDate = self.histData[-2]['date']
        self.stockId = stockDf['stock_id'].to_list()[0]
        self.tradeDate = stockDf['date'].to_list()[-1]

    def getPenFromDate(self, date):
        for i in range(len(self.penList)):
            pen = self.penList[i]
            if pen['startDate'] == date:
                startPen = self.penList[i-1]
                endPen = self.penList[i]
                return (startPen, endPen)
        return (None,None)

    def convertDfToHistData(self, stockDf):
        if isinstance(stockDf,pd.DataFrame):
            return stockDf.to_dict(orient ='records')
        return stockDf

    def isPenBuyPoint(self):
        if self.penList is None or len(self.penList) == 0:
            return False
        lastPen = self.penList[-1]
        if lastPen['type'] == PenType.down and lastPen['endSimplifyIndex'] == len(self.simplifyData) - 2:
            return self.simplifyData[-1]['date'] == self.histData[-1]['date']
        return False

    def isPenSellPoint(self):
        if self.penList is None or len(self.penList) == 0:
            return False
        lastPen = self.penList[-1]
        if lastPen['type'] == PenType.up and lastPen['endSimplifyIndex'] == len(self.simplifyData) - 2:
            return self.simplifyData[-1]['date'] == self.histData[-1]['date']
        return False

    def run(self, backTest = False):
        self.simplifyData = SimplifyLogic.simplifyHistData(self.histData)
        self.partingList = PartingLogic.getPartingList(self.simplifyData)
        if backTest:
            if not self.isLastParting():
                return False
        self.penList = PenLogic.createPenList(self.partingList)
        self.baseSegmentList = SegmentLogic.createSegmentList(self.penList)
        self._initSegmentDic()
        self._initCentreDic()
        self._initPenCentre()

        return True
        #self.buyPoint = BuyPointLogic.getThirtyLevelBuyPoint(self.segmentDic,self.endDateStr)
        #self.buyPointFive = BuyPointLogic.getThirtyLevelBuyPoint(self.segmentDic,self.endDateStr,'5')
        #self._initBuyPoints()

    def genPenSellFeature(self):
        feature = {}
        lastPen = self.penList[-1]
        feature['stock_id'] = self.stockId
        feature['trade_date'] = self.tradeDate
        feature['sell_pen_date'] = lastPen['endDate']
        feature['sell_pen_value'] = lastPen['endDate']
        feature['sell_date'] = self.histData[-1]['date']
        feature['sell_value'] = self.histData[-1]['close']
        feature['sell_before_pen_date'] = self.penList[-1]['startDate']
        return feature

    def getHistDataIndexFromDate(self, histDate):
        for i in range(len(self.histData)):
            if self.histData[i]['date'] == histDate:
                return i
        return -1

    def isPenChange(self):
        if self.penList is None:
            return False
        lastPen = self.penList[-1]
        if lastPen['endSimplifyIndex'] == len(self.simplifyData) - 3:
            #print 'pen change'
            return True
        return False

    def getBuyPointsCount(self):
        count = 0
        for freq in self.segmentDic.keys():
            if self.segmentDic[freq] is not None and len(self.segmentDic[freq]) > 0:
                lastSegmentEndDateStr = DateUtils.convertTimestampToStr(self.segmentDic[freq][-1]['endDate'])
                if lastSegmentEndDateStr[0:10] == self.endDateStr[0:10] and self.segmentDic[freq][-1]['type'] == PenType.down:
                    count += 1
        return count

    def getLastPen(self):
        return self.penList[-1]

    def isSegmentChange(self,freq='1'):
        if self.segmentDic is None or not self.segmentDic.has_key(freq) or self.segmentDic[freq] is None:
            return False
        lastSegment = self.segmentDic[freq][-1]
        if lastSegment['endSimplifyIndex'] == len(self.simplifyData) - 3:
            return True
        return False

    def getLastSegment(self,freq='1'):
        return self.segmentDic[freq][-1]

    def _initSegmentDic(self):
        self.segmentDic = {}
        subFreq = FreqUtils.getSubFreq(self.baseFreq)
        self.segmentDic[subFreq] = self.penList
        self.segmentDic[self.baseFreq] = self.baseSegmentList
        currentFreq = self.baseFreq
        superFreq = FreqUtils.getSuperFreq(self.baseFreq)
        while superFreq is not None and superFreq != FreqUtils.getSuperFreq(self.rootFreq):
            currentSegment = self.segmentDic[currentFreq]
            superSegment = SegmentLogic.createSegmentList(currentSegment)
            self.segmentDic[superFreq] = superSegment
            currentFreq = superFreq
            superFreq = FreqUtils.getSuperFreq(currentFreq)

    def _initCentreDic(self):
        self.centreDic = {}
        currentFreq = self.baseFreq
        superFreq = FreqUtils.getSuperFreq(currentFreq)
        while superFreq is not None and self.segmentDic.__contains__(superFreq):
            currentSegment = self.segmentDic[currentFreq]
            superSegment = self.segmentDic[superFreq]
            centreList = CentreLogic.createCentreList(superSegment,currentSegment)
            self.centreDic[currentFreq] = centreList
            currentFreq = superFreq
            superFreq = FreqUtils.getSuperFreq(currentFreq)

    def _initPenCentre(self):
        baseSegment = self.segmentDic[self.baseFreq]
        self.penCentre = CentreLogic.createCentreList(baseSegment, self.penList)
        self.centreDic['pen'] = self.penCentre


    def getSegment(self,freq):
        if self.segmentDic.__contains__(freq):
            return self.segmentDic[freq]
        return None

    def getCentre(self,freq):
        if self.centreDic.__contains__(freq):
            return self.centreDic[freq]
        return None

    def isLastParting(self):
        if self.partingList is None or len(self.partingList) == 0:
            return False
        lastParting = self.partingList[-1]
        return lastParting['simplifyIndex'] == len(self.simplifyData) -2


    def genPenFeatures(self):
        feature = {}
        lastPen = self.penList[-1]
        lastPenType = lastPen['type']
        penEndDate = lastPen['endDate']
        penStartValue = lastPen['startValue']
        penEndValue = lastPen['endValue']
        isLastPenPoint = penEndDate == self.lastDate
        isPenBuyPoint = (lastPenType == PenType.down and isLastPenPoint)
        isPenSellPoint = (lastPenType == PenType.up and isLastPenPoint)
        penChgRatio = (penEndValue - penStartValue) / penStartValue * 100
        penHistNum = lastPen['endOrginIndex'] - lastPen['startOrginIndex'] + 1
        penChgVelocity = penChgRatio / penHistNum
        penPartingNum = lastPen['endPartingIndex'] - lastPen['startPartingIndex'] + 1
        penPartingList = self.partingList[lastPen['startPartingIndex']:lastPen['endPartingIndex']]
        penUpPartingNum = 0
        penDownPartingNum = 0
        for parting in penPartingList:
            type = parting['type']
            if type == PartingType.down:
                penDownPartingNum += 1
            if type == PartingType.up:
                penUpPartingNum += 1
        feature['is_last_pen_point'] = isLastPenPoint
        feature['is_pen_buy_point'] = isPenBuyPoint
        feature['is_pen_sell_point'] = isPenSellPoint
        feature['pen_chg_ratio'] = penChgRatio
        feature['pen_chg_velocity'] = penChgVelocity
        feature['pen_parting_num'] = penPartingNum
        feature['pen_hist_num'] = penHistNum
        feature['pen_up_parting_num'] = penUpPartingNum
        feature['pen_down_parting_num'] = penDownPartingNum
        feature['pen_end_date'] = penEndDate
        return feature

    def genPartingFeature(self):
        lastParting = self.partingList[-1]
        feature = {}
        feature['parting_type'] = lastParting['type']
        feature['parting_right_mid_high_chg'] = (lastParting['rightHigh'] - lastParting['midHigh']) / lastParting['midHigh'] * 100
        feature['parting_right_mid_low_chg'] = (lastParting['rightLow'] - lastParting['midLow']) / lastParting['midLow'] * 100
        feature['parting_right_left_high_chg'] = (lastParting['rightHigh'] - lastParting['leftHigh']) / lastParting['midHigh'] * 100
        feature['parting_right_left_low_chg'] = (lastParting['rightLow'] - lastParting['leftLow']) / lastParting['midLow'] * 100
        feature['parting_mid_left_high_chg'] = (lastParting['midHigh'] - lastParting['leftHigh']) / lastParting['midHigh'] * 100
        feature['parting_mid_left_low_chg'] = (lastParting['midLow'] - lastParting['leftLow']) / lastParting['midLow'] * 100
        high = max([lastParting['leftHigh'],lastParting['midHigh'],lastParting['rightHigh']])
        low = min([lastParting['leftLow'],lastParting['midLow'],lastParting['rightLow']])
        feature['parting_chg_ratio'] = (high - low) / low * 100
        feature['parting_left_chg'] = (lastParting['leftHigh'] - lastParting['leftLow']) / lastParting['leftLow'] * 100
        feature['parting_mid_chg'] = (lastParting['midHigh'] - lastParting['midLow']) / lastParting['midLow'] * 100
        feature['parting_right_chg'] = (lastParting['rightHigh'] - lastParting['rightLow']) / lastParting['rightLow'] * 100
        feature['parting_right_low_mid_high_chg'] = (lastParting['rightLow'] - lastParting['midHigh']) / lastParting['rightLow'] * 100
        feature['parting_left_low_mid_high_chg'] = (lastParting['leftLow'] - lastParting['midHigh']) / lastParting['midHigh'] * 100
        return feature

    def genSegmentFeature(self,freq):
        segmentList = self.segmentDic[freq]
        feature = {}
        freqLower = str(freq).lower()
        if segmentList is None or len(segmentList) == 0:
            feature['%s_is_last_segment_point' % (freqLower)] = None
            feature['%s_is_segment_buy_point' % (freqLower)] = None
            feature['%s_is_segment_sell_point' % (freqLower)] = None
            feature['%s_segment_chg_ratio' % (freqLower)] = None
            feature['%s_segment_chg_velocity' % (freqLower)] = None
            feature['%s_segment_pen_num' % (freqLower)] = None
            feature['%s_segment_centre_num' % (freqLower)] = None
            feature['%s_segment_bar_num' % (freqLower)] = None
            return feature
        lastSegment = segmentList[-1]
        lastSegmentType = lastSegment['type']
        endDate = lastSegment['endDate']
        startValue = lastSegment['startValue']
        endValue = lastSegment['endValue']
        isLastSegmentPoint = endDate == self.lastDate
        isSegmentBuyPoint = (lastSegmentType == PenType.down and isLastSegmentPoint)
        isPenSellPoint = (lastSegmentType == PenType.up and isLastSegmentPoint)
        segmentChgRatio = (endValue - startValue) / startValue * 100
        segmentHistNum = lastSegment['endOrginIndex'] - lastSegment['startOrginIndex'] + 1
        segmentChgVelocity = segmentChgRatio / segmentHistNum
        segmentPenNum = lastSegment['endPenIndex'] - lastSegment['startPenIndex'] + 1

        feature['%s_is_last_segment_point' % (freqLower)] = isLastSegmentPoint
        feature['%s_is_segment_buy_point' % (freqLower)] = isSegmentBuyPoint
        feature['%s_is_segment_sell_point' % (freqLower)] = isPenSellPoint
        feature['%s_segment_chg_ratio' % (freqLower)] = segmentChgRatio
        feature['%s_segment_chg_velocity' % (freqLower)] = segmentChgVelocity
        feature['%s_segment_pen_num' % (freqLower)] = segmentPenNum
        feature['%s_segment_centre_num' % (freqLower)] = lastSegment['centerNum']
        feature['%s_segment_bar_num' % (freqLower)] = segmentHistNum
        return feature

    def genCentreFeature(self,freq):
        feature = {}
        freqLower = str(freq).lower()
        if not self.centreDic.__contains__(freq) or self.centreDic[freq] is None or len(self.centreDic[freq]) == 0:
            feature['%s_centre_chg_ratio' % (freqLower)] = None
            feature['%s_centre_extreme_chg_ratio' % (freqLower)] = None
            feature['%s_centre_hist_num' % (freqLower)] = None
            feature['%s_centre_pen_num' % (freqLower)] = None
            feature['%s_pen_to_centre_upper' % (freqLower)] = None
            feature['%s_pen_to_centre_lower' % (freqLower)] = None
            feature['%s_pen_to_centre_extreme_upper' % (freqLower)] = None
            feature['%s_pen_to_centre_extreme_lower' % (freqLower)] = None
            return feature
        centreList = self.centreDic[freq]
        lastCentre = centreList[-1]
        low = lastCentre['low']
        high = lastCentre['high']
        extremeLow = lastCentre['extremeLow']
        extremeHigh = lastCentre['extremeHigh']
        feature['%s_centre_chg_ratio' % (freqLower)] = (high - low) / low * 100
        feature['%s_centre_extreme_chg_ratio' % (freqLower)] = (extremeHigh - extremeLow) / extremeLow * 100
        feature['%s_centre_hist_num' % (freqLower)] = lastCentre['endOrginIndex'] - lastCentre['startOrginIndex'] + 1
        feature['%s_centre_pen_num' % (freqLower)] = lastCentre['endPenIndex'] - lastCentre['startPenIndex'] + 1
        lastPen = self.penList[-1]
        lastPenValue = lastPen['endValue']
        feature['%s_pen_to_centre_upper' % (freqLower)] = (lastPenValue - high) / high * 100
        feature['%s_pen_to_centre_lower' % (freqLower)] = (lastPenValue - low) / low * 100
        feature['%s_pen_to_centre_extreme_upper' % (freqLower)] = (lastPenValue - extremeHigh) / extremeHigh * 100
        feature['%s_pen_to_centre_extreme_lower' % (freqLower)] = (lastPenValue - extremeLow) / extremeLow * 100
        return feature

    def genFeature(self):
        feature = {}
        if self.penList is None or len(self.penList) == 0:
            return {}
        feature['stock_id'] = self.stockId
        feature['trade_date'] = self.tradeDate
        feature['buy_pen_date'] = self.penList[-1]['endDate']
        feature['buy_pen_value'] = self.penList[-1]['endValue']
        partingFeature = self.genPartingFeature()
        penFeature = self.genPenFeatures()
        segmentFeatureD = self.genSegmentFeature('D')
        #segmentFeatureW = self.genSegmentFeature('W')
        centreFeaturePen = self.genCentreFeature('pen')
        centreFeatureD = self.genCentreFeature('D')
        barFeature = self.genBarFeature()
        feature.update(partingFeature)
        feature.update(penFeature)
        feature.update(segmentFeatureD)
        #feature.update(segmentFeatureW)
        feature.update(centreFeatureD)
        feature.update(centreFeaturePen)
        feature.update(barFeature)
        return feature

    def genBarFeature(self):
        feature = {}
        bar = self.histData[-1]
        beforeBar = self.histData[-2]
        barOpenChg = (bar['open'] - beforeBar['close']) / beforeBar['close'] * 100
        barMaxChg = (bar['high'] - bar['low']) / bar['low'] * 100
        barMaxToPartingChg = (bar['high'] - beforeBar['low']) / beforeBar['low'] * 100
        barHighToCloseChg = (bar['high'] - bar['close']) / bar['close'] * 100
        barCloseToLowChg = (bar['close'] - bar['low']) / bar['low'] * 100
        barCloseToOpenChg = (bar['close'] - bar['open']) / bar['open'] * 100
        avgPrice = (bar['high'] + bar['low']) / 2
        barCloseToMinChg = (bar['close'] - avgPrice) / avgPrice * 100
        feature['bar_open_chg'] = barOpenChg
        feature['bar_max_chg'] = barMaxChg
        feature['bar_max_to_parting_chg'] = barMaxToPartingChg
        feature['bar_high_to_close_chg'] = barHighToCloseChg
        feature['bar_close_to_low_chg'] = barCloseToLowChg
        feature['bar_close_to_open_chg'] = barCloseToOpenChg
        feature['bar_close_to_min_chg'] = barCloseToMinChg
        return feature

'''
    def _initBuyPoints(self):
        freq = FreqUtils.getSubFreq(self.rootFreq)
        while freq != self.baseFreq:
            self._initBuyPointsFreq(freq)
            freq = FreqUtils.getSubFreq(freq)

    def _initBuyPointsFreq(self,freq):
        self.buyPoints[freq] = {}
        self._initFisrtBuy(freq)
        self._initSecondBuy(freq)
        self._initThirdBuy(freq)

    def _initFisrtBuy(self,freq):
        superFreq = FreqUtils.getSuperFreq(freq)
        if not self.segmentDic.has_key(superFreq):
            return
        superSegment = self.segmentDic[superFreq]
        if superSegment is None or len(superSegment) == 0:
            return
        lastTrend = superSegment[-1]
        if lastTrend['type'] == PenType.up:
            return
        if self._isSegmentsDownDeparture(freq,lastTrend):
            buyPoint = {}
            buyPoint['type'] = BuyPointsType.firstBuy
            buyPoint['date'] = lastTrend['endDate']
            buyPoint['value'] = lastTrend['endValue']
            buyPoint['orginIndex'] = lastTrend['endOrginIndex']
            buyPoint['segmentIndex'] = lastTrend['endPenIndex']
            buyPoint['freq'] = freq
            buyDic = self.buyPoints[freq]
            buyDic[BuyPointsType.firstBuy] = buyPoint

    def _initSecondBuy(self,freq):
        if not self.buyPoints.has_key(freq):
            return
        buyDic = self.buyPoints[freq]
        if buyDic is None or not buyDic.has_key(BuyPointsType.firstBuy):
            return
        firstBuy = buyDic[BuyPointsType.firstBuy]
        firstBuySegmentIndex = firstBuy['segmentIndex']
        segmentList = self.getSegment(freq)
        if firstBuySegmentIndex + 2 > len(segmentList) - 1:
            return None
        secondBuySegment = segmentList[firstBuySegmentIndex + 2]
        subFreq = FreqUtils.getSubFreq(freq)
        if self._isSegmentsDownDeparture(subFreq,secondBuySegment):
            lastCentre = self.getCentre(freq)[-1]
            buyType = BuyPointsType.secondBuy
            if secondBuySegment['endValue'] > lastCentre['high']:
                buyType = BuyPointsType.secondThirdBuy
            buyPoint = {}
            buyPoint['type'] = buyType
            buyPoint['date'] = secondBuySegment['endDate']
            buyPoint['value'] = secondBuySegment['endValue']
            buyPoint['orginIndex'] = secondBuySegment['endOrginIndex']
            buyPoint['segmentIndex'] = secondBuySegment['index']
            buyPoint['freq'] = freq
            buyDic[buyType] = buyPoint

    def _initThirdBuy(self,freq):
        superFreq = FreqUtils.getSuperFreq(freq)
        if not self.segmentDic.has_key(superFreq):
            return
        superSegment = self.segmentDic[superFreq]
        if superSegment is None or len(superSegment) == 0:
            return
        lastTrend = superSegment[-1]
        if lastTrend['type'] == PenType.down:
            return
        segmentList = self.getSegment(freq)
        thirdSegmentIndex = lastTrend['endPenIndex'] + 1
        if thirdSegmentIndex > len(segmentList) - 1:
            return
        thirdSegment = segmentList[thirdSegmentIndex]
        centreList = self.getCentre(freq)
        if centreList is None or len(centreList) == 0:
            return
        lastCentre = centreList[-1]
        if thirdSegment['endValue'] < lastCentre['high']:
            return
        subFreq = FreqUtils.getSubFreq(freq)
        if self._isSegmentsDownDeparture(subFreq,thirdSegment):
            buyPoint = {}
            buyPoint['type'] = BuyPointsType.thirdBuy
            buyPoint['date'] = thirdSegment['endDate']
            buyPoint['value'] = thirdSegment['endValue']
            buyPoint['orginIndex'] = thirdSegment['endOrginIndex']
            buyPoint['segmentIndex'] = thirdSegment['endPenIndex']
            buyPoint['freq'] = freq
            buyDic = self.buyPoints[freq]
            buyDic[BuyPointsType.thirdBuy] = buyPoint


    def _isSegmentsDownDeparture(self,freq,superTrend):
        if not self.centreDic.has_key(freq):
            return False
        centreList = self.getCentre(freq)
        if centreList is None or len(centreList) == 0:
            return False
        lastCentre = None
        for i in range(0,len(centreList))[::-1]:
            if centreList[i]['segmentIndex'] == superTrend['index'] and centreList[i]['endPenIndex'] < superTrend['endPenIndex']:
                lastCentre = centreList[i]
                break
        if lastCentre is None:
            return False
        segmentList = self.getSegment(freq)
        if lastCentre['endPenIndex'] + 1 >= len(segmentList):
            return False
        beforeSegment = segmentList[lastCentre['startPenIndex'] - 1]
        afterSegment = segmentList[lastCentre['endPenIndex'] + 1]
        leftArea = self.macdLogic.getMacdArea(beforeSegment['startDate'],beforeSegment['endDate'],True,False)
        rightArea = self.macdLogic.getMacdArea(afterSegment['startDate'],afterSegment['endDate'],False,False)
        leftSignalDiff = self.macdLogic.getExtremeMacdSignalDiff(beforeSegment['startDate'],beforeSegment['endDate'])
        rightSignalDiff = self.macdLogic.getExtremeMacdSignalDiff(afterSegment['startDate'],afterSegment['endDate'])
        currentIsDeparture = (rightArea < leftArea) and (rightSignalDiff < leftSignalDiff)
        if currentIsDeparture:
            subFreq = FreqUtils.getSubFreq(freq)
            if not self.segmentDic.has_key(subFreq):
                return True
            else:
                return self._isSegmentsDownDeparture(subFreq,segmentList[-1])
        else:
            return False

    def getBuyPoints(self,freq):
        if not self.buyPoints.has_key(freq):
            return None
        return self.buyPoints[freq]

    def isReadyToBuy(self,freq):
        buyPoints = self.getBuyPoints(freq)
        if buyPoints is None:
            return False
        if buyPoints['orginIndex'] == len(self.histData) - 2:
            return True
        else:
            return False

    def getLastBuyPoint(self,freq):
        return self.getBuyPoints(freq)
'''


