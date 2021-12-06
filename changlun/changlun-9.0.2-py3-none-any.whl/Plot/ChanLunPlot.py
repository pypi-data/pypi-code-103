from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Scatter

import UtilTools.DateUtils as DateUtils
from ChangLunLogic.Model import *


class ChanLunPlot():
    def __init__(self, chanLunRecursieLogic):
        self.features = None
        self.chunLunModel = chanLunRecursieLogic

    def setFeatures(self,features):
        self.features = features

    def plot(self, basePath = 'D:\\stock\\'):
        simplifyBars = self.getSimplifyLines()
        penLine = self.getPenLines()
        if penLine is not None:
            simplifyBars.overlap(penLine)
        segmentLines = self.getSegmentLines()
        if segmentLines is not None:
            for line in segmentLines:
                simplifyBars.overlap(line)
        if self.features is not None:
            simplifyBars.overlap(self.getHistBuyPoints())
            simplifyBars.overlap(self.getHistSellPoints())
        simplifyBars.render('%s\\%s.html' % (basePath,self.chunLunModel.stockId))

    def save(self, path=None, endDate=None):
        if path is None:
            if endDate is None:
                endDate = DateUtils.getTodayStr()
            basePath = 'D:\\xampp\\htdocs\\model\\%s' % (endDate)
            if self.chunLunModel.buyPoint is not None:
                simpleBuyPoint = BuyPointsType.getBuyPointSimple(self.chunLunModel.buyPoint.type)
            else:
                simpleBuyPoint = 9
            path = '%s\\%s_%s%s.html' % (
            basePath, str(simpleBuyPoint), self.chunLunModel.stockId, self.chunLunModel.name)
        print(path)
        self.overlap.render(path)

    def plotHistBuyPoint(self, buyPoints):
        if buyPoints is None or len(buyPoints) == 0:
            return
        buyPointDic = {}
        for x in buyPoints:
            type = x['type']
            date = x['date']
            value = x['value']
            if buyPointDic.__contains__(type):
                buyPointDic[type][0].append(date)
                buyPointDic[type][1].append(value)
            else:
                buyPointDic[type] = ([], [])
        for type in buyPointDic.keys():
            pointPlot = Scatter()
            pointPlot.add(type, buyPointDic[type][0], buyPointDic[type][1])
            self.overlap.add(pointPlot)

    def getSimplifyLines(self):
        olchList = []
        datetimeList = []
        for bar in self.chunLunModel.histData:
            barDate = DateUtils.convertTimestampToStr(bar['date'])
            olch = [bar['open'], bar['close'], bar['low'], bar['high']]
            datetimeList.append(barDate)
            olchList.append(olch)
        kline = (
            Kline(
                init_opts=opts.InitOpts(width="100%",height="600px")
            ).add_xaxis(xaxis_data=datetimeList)
                .add_yaxis(series_name='', y_axis=olchList, itemstyle_opts=opts.ItemStyleOpts(
                color="#ef232a",
                color0="#14b143",
                border_color="#ef232a",
                border_color0="#14b143",
            )).set_global_opts(
                xaxis_opts=opts.AxisOpts(is_scale=True),
                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),
                datazoom_opts=[opts.DataZoomOpts(range_start=80,range_end=100)],
                title_opts=opts.TitleOpts(title=self.chunLunModel.stockId),

            )
        )

        centre = self.getPenCentreMarkItemAreas()
        if centre is not None and len(centre) > 0:
            kline.set_series_opts(
                markarea_opts=opts.MarkAreaOpts(data=centre)
            )

        return kline

    def getPenLines(self):
        penList = self.chunLunModel.penList
        if penList is None or len(penList) == 0:
            return None

        x = []
        y = []
        for pen in penList:
            startDate = DateUtils.convertTimestampToStr(pen['startDate'])
            x.append(startDate)
            y.append(pen['startValue'])
        endDate = DateUtils.convertTimestampToStr(penList[-1]['endDate'])
        x.append(endDate)
        y.append(penList[-1]['endValue'])
        penLine = (
            Line()
                .add_xaxis(xaxis_data=x)
                .add_yaxis(series_name='pen', y_axis=y)
        )
        return penLine

    def getSegmentLines(self):
        segmentDic = self.chunLunModel.segmentDic
        if segmentDic is None or len(segmentDic) == 0:
            return None
        segmentLines = []

        for freq in segmentDic.keys():
            if segmentDic[freq] is None or freq == '1':
                continue
            title = 'seg_%s' % (freq)
            x = []
            y = []
            for pen in segmentDic[freq]:
                startDate = DateUtils.convertTimestampToStr(pen['startDate'])
                x.append(startDate)
                y.append(pen['startValue'])
            endDate = DateUtils.convertTimestampToStr(segmentDic[freq][-1]['endDate'])
            x.append(endDate)
            y.append(segmentDic[freq][-1]['endValue'])
            segmentLine = (
                Line()
                    .add_xaxis(xaxis_data=x)
                    .add_yaxis(series_name=title, y_axis=y)
            )
            segmentLines.append(segmentLine)
        return segmentLines

    def getCentreMarkItemAreas(self,freq):
        centreList = self.chunLunModel.centreDic.get(freq)
        if centreList is None or len(centreList) == 0:
            return None
        area = []
        for centre in centreList:
            x = (centre['startDate'], centre['endDate'])
            y = (centre['low'],centre['high'])
            area.append( opts.MarkAreaItem(x=x,y=y) )
        return area

    def getPenCentreMarkItemAreas(self):
        if self.chunLunModel.penCentre is None or len(self.chunLunModel.penCentre) == 0:
            return None
        area = []
        for centre in self.chunLunModel.penCentre:
            x = (centre['startDate'], centre['endDate'])
            y = (centre['low'],centre['high'])
            area.append( opts.MarkAreaItem(x=x,y=y) )
        return area

    def getHistBuyPoints(self):
        x = [x['buy_pen_date'] for x in self.features]
        y = [x['buy_pen_value'] for x in self.features]
        scatter = (
            Scatter().add_xaxis(xaxis_data=x)
            .add_yaxis(series_name='历史买点',y_axis=y)
        )
        return scatter

    def getHistSellPoints(self):
        x = [x['sell_date'] for x in self.features]
        y = [x['sell_value'] for x in self.features]
        scatter = (
            Scatter().add_xaxis(xaxis_data=x)
            .add_yaxis(series_name='历史卖点',y_axis=y)
        )
        return scatter
