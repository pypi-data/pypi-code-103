# -*- coding: utf-8 -*-
from tradeTools import helpers
from tradeTools import Decorator
from tmqc.frame import data_center
from tmqc.frame import stock_func
from datetime import datetime
import pandas as pd
import numpy as np

class Mgr():
    def __init__(self):
        self.oldDc = data_center.use()

    def queryST(self, dateTime = 20210101):
        # 用连续两年的年报日期的数据来判断ST
        reportYear = dateTime // 10000 - 1 if dateTime % 10000 >= 430 else dateTime // 10000 - 2
        queryConf = {}
        queryConf["RecurringNetProfit"] = "扣除非经常性损益后的净利润"
        reportDate = reportYear * 10000 + 1231
        lastReportDate = (reportYear - 1) * 10000 + 1231
        sql = "SELECT "
        for key in queryConf.keys():
            sql += key + ","
        sql += f"symbol,reportDate FROM `income` WHERE reportDate in ({reportDate},{lastReportDate}) "
        df = pd.read_sql(sql, self.oldDc.database.conn)
        df = df.set_index("symbol")
        stSymbols = []
        for symbol in set(df.index.tolist()):
            _df = df.loc[symbol, ["RecurringNetProfit"]]
            __df = _df[_df.values > 0]  # 两年全负数，
            if __df.empty:
                stSymbols.append(symbol)
        return stSymbols
    # 获取上市满1年的股票
    # 过滤st股
    def getSymbols(self,dateTime = 20210101):
        if not hasattr(self, 'listDf'):
            self.listDf = helpers.getSymbolsInfo()
            self.listDf = self.listDf.drop_duplicates(subset=["symbol",],keep='first')
            self.listDf = self.listDf.set_index("symbol")
            listDf = self.listDf
        else:
            listDf = self.listDf
        start = datetime.strptime(str(dateTime), '%Y%m%d') + pd.tseries.offsets.DateOffset(years = -1)
        symbols= listDf[listDf.listingDate<=start].index.tolist()
        symbols = list(set(symbols) - set(self.queryST(dateTime =dateTime)))
        return symbols
    
    @Decorator.loadData(path="data")
    def genIDXData(self, indexSymbol, frequency,isRealTime = False):
        # 获取指数月度收益率数据
        # fileExtension ：间隔日
        if not hasattr(self, "oldDc"):
            self.oldDc = data_center.use()
        sql = "SELECT "
        sql += f" code,time,close from `index_day_data` WHERE code = '{indexSymbol}'"
        df = pd.read_sql(sql, self.oldDc.database.conn)
        df['date'] = pd.to_datetime(df['time'], format='%Y%m%d')
        df.set_index('date', inplace=True)

        tradeDaysDf = self.genTradeDays(frequency=frequency,isRealTime = isRealTime)
        conDf = pd.concat([tradeDaysDf, df], join="inner", axis=1)
        conDf[indexSymbol] = conDf.close / conDf.close.shift(1) - 1
        return conDf

    @Decorator.loadData(path="data")
    def genSymbolRateData(self, symbol, frequency, isRealTime=False):
        # 生成间隔数据收益率数据
        if not hasattr(self, "oldDc"):
            self.oldDc = data_center.use()
        sql = "SELECT "
        sql += f" code,time,close,volume from `tdx_day_data` WHERE code = '{symbol}'"
        df = pd.read_sql(sql, self.oldDc.database.conn)
        df['date'] = pd.to_datetime(df['time'], format='%Y%m%d')
        df.set_index('date', inplace=True)
        if df.empty:
            return pd.DataFrame()
        tradeDaysDf = self.genTradeDays(frequency=frequency, isRealTime=isRealTime)
        _tradeDaysDf = tradeDaysDf[tradeDaysDf.index >= df.iloc[0].name]  # 截取该股票的上市之后的交易日
        df = pd.merge(_tradeDaysDf, df, how="left", left_on="交易日", right_on="time")  # 已分割交易日和k线合并
        df['date'] = pd.to_datetime(df['交易日'], format='%Y%m%d')
        df.set_index('date', inplace=True)
        
        df["lastTime"] = df.time.shift()
        df["lastClose"] = df.close.shift()

        def _getRehabilitationClose(hang):  # 复权
            begTime = hang.lastTime
            endTime = hang.time
            symbol = hang.code
            dividends = self.oldDc.query_dividends(stock_id=symbol, begtime=begTime, endtime=endTime)
            pre_close = hang.lastClose
            if dividends[symbol]:
                for dividend in dividends[symbol]:
                    pre_close = stock_func.get_dividend_pre_price(pre_close, dividend[1])  # 前复权
            return (hang.close / pre_close) - 1

        # 如果交易日停牌。则当日和下一个间隔交易日收益率为空
        df["mRate"] = df.apply(_getRehabilitationClose, axis=1)
        

        sql = "SELECT "
        sql += f" id,datetime,total_capital,unlimited_sell_shares from `std_dzh_capital_report` WHERE id = '{symbol}'"
        capital = pd.read_sql(sql, self.oldDc.database.conn)
        capital['date'] = pd.to_datetime(capital['datetime'], format='%Y%m%d')
        capital.set_index('date', inplace=True)
        capital = capital[["total_capital","unlimited_sell_shares"]]/10**4
        conDf = pd.concat([df, capital], join="outer", axis=1)
        conDf["total_capital"].fillna(method='ffill', inplace=True)  # ’ffill’，向前填充，或是向下填充
        conDf["unlimited_sell_shares"].fillna(method='ffill', inplace=True)  # ’ffill’，向前填充，或是向下填充

        conDf["MarketV"] = conDf["close"]*conDf["total_capital"]
        conDf["MarketV"].fillna(method='ffill', inplace=True)  # ’ffill’，向前填充，或是向下填充
        conDf["TurnOver"] = conDf["volume"]*100/conDf["unlimited_sell_shares"]*100
        conDf = conDf.dropna(axis=0,subset = ["交易日"]) 
        return conDf

    @Decorator.loadData(path="data")
    def genSymbolTScore(self, symbol, frequency,windows,):#滚动z分数
        allData = self.genSymbolRateData(symbol=symbol,frequency=frequency)
        if allData.empty:
            return pd.DataFrame()
        allData['mRate'].fillna(0, inplace=True) # 停牌的日期。收益率为设为0
        allData['mean'] = allData['mRate'].rolling(windows).mean()
        allData['std'] = allData['mRate'].rolling(windows).std(ddof = 1)
        allData["ZScore"] =  (allData['mRate'] - allData['mean'])/allData['std']
        allData["TScore"] =  50+10*allData["ZScore"]
        return allData[['mRate','mean','std','ZScore','TScore']]

    @Decorator.loadData(path="data")
    def genTradeDays(self,frequency :int = 20,isRealTime = False):
        # 根据换仓频率生成交易日列表
        # fileExtension 交易日间隔
        allTradeDays =  self.oldDc.trade_days
        # 切割交易日
        tradeDays = []
        for i in range(len(allTradeDays)//frequency+1):
            index =  (i+1)*frequency-1
            if index < len(allTradeDays):
                tradeDays.append(allTradeDays[index])
        df = pd.DataFrame(tradeDays,columns=["交易日"])
        df['date'] = pd.to_datetime(df['交易日'], format='%Y%m%d')
        df.set_index('date', inplace=True)
        return df

    def getSymbolRateData(self,symbol, frequency=1,isRealTime=False):
        if not hasattr(self, 'symbolRateData'):
                self.symbolRateData = {}
        if symbol not in self.symbolRateData:
            symbolRateData = self.genSymbolRateData(symbol=symbol, frequency=1,
                                                isRealTime=isRealTime)
            if symbolRateData.empty:
                print(f"{symbol}无历史行情数据")
            self.symbolRateData[symbol] = symbolRateData
        return self.symbolRateData.get(symbol)
    
    def genReturn(self,beg,end,symbols,weight = []):
        rate = []
        for symbol in symbols:
            df = self.getSymbolRateData(symbol=symbol,frequency=1)
            # 计算累计收益率
            s = df.loc[(beg<df.index) & (df.index<=end)]["mRate"] 
  
            s.name = symbol
            rate.append(s)
        rateDf = pd.concat(rate,axis=1)
        rateDf = rateDf.fillna(0)  # 停牌股。当日的收益率为0
        # 如果多个交易日。由初始交易日的权重和前一日的净值。得出前一日的权重比例。再和当日的收益率点积
        if rateDf.shape[0] <= 1:
            rate = np.dot(rateDf.iloc[-1],weight)  
        else :
            cumprodDf  =(1 + rateDf).cumprod()
            last = cumprodDf.iloc[-1]
            # 考虑如果总仓位累加不为1
            _p = 1- np.sum(weight) # 初始留存的净值
            rate = _p+np.dot(cumprodDf.iloc[-1],weight) # 当前净值
            rate/= _p+ np.dot(cumprodDf.iloc[-2],weight)# 上一日净值    
            rate -= 1       
        return rate
    # 计算symbols组合的收益率
    def genReturnMonthlys(self, dateTime, symbols, frequency, ):
        seriseMonthRate = []
        for symbol in symbols:
            if not hasattr(self, 'symbolRateData'):
                self.symbolRateData = {}

            if symbol not in self.symbolRateData:
                symbolRateData = self.genSymbolRateData(symbol=symbol, frequency=frequency,
                                                        isRealTime=False)
                if symbolRateData.empty:
                    continue
                symbolRateData["lastMarketV"] = symbolRateData["MarketV"].shift()
                symbolRateData['lastMarketV'].fillna(method='ffill', inplace=True)  # ’ffill’，向前填充，或是向下填充
                self.symbolRateData[symbol] = symbolRateData
            df = self.symbolRateData.get(symbol)

            if dateTime not in df.index:
                print(f"{symbol} {dateTime}的数据为空 ")
                continue
            s = df.loc[dateTime]
            seriseMonthRate.append(s)
        monthDf = pd.DataFrame(seriseMonthRate)
        if monthDf.empty:
            return monthDf
        monthDf["市值权重"] = monthDf.lastMarketV / monthDf.lastMarketV.sum()
        monthDf["wRate"] = monthDf.mRate * monthDf["市值权重"]  # 加权收益率
        print(monthDf)
        sumWRate = monthDf.wRate.sum()
        meanRate = monthDf.mRate.mean()
        returnMonthlyDf = pd.DataFrame([[sumWRate, meanRate]], index=[dateTime], columns=['sumWRate', "meanRate"])
        return returnMonthlyDf

if __name__ == '__main__':
    m = Mgr()
    CON_FREQUENCY = 1
    CON_INDEX_SYMBOL = "SH.000300"
    # idxDf =  m.genIDXData(indexSymbol= CON_INDEX_SYMBOL, frequency=CON_FREQUENCY)
    # print(idxDf)

    # symbolTScore = m.genSymbolTScore(symbol="SH.600000", frequency =1,windows =30)
    # r = m.genSymbolRateData(symbol = "SZ.300492", frequency =20, isRealTime=True)
    # print(r)
    
    # r = m.genReturn(beg =pd.to_datetime(20070521, format='%Y%m%d'),
    #                 end =pd.to_datetime(20070522, format='%Y%m%d'),
    #                 symbols=["SH.600000","SH.600019"],weight=[0.5,0.5,])
    a  =5 
    a /= 2+1
    print(a)