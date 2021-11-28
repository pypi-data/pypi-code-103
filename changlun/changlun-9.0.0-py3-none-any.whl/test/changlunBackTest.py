from UtilTools.impalaUtils import getDfFromSql, refreshTable
from ChangLunLogic.changLunBackTest import getHistTradeFeatures
from ChangLunLogic.ChangLun import ChangLun
from Plot.ChanLunPlot import ChanLunPlot
import pandas as pd
from UtilTools.mysqlClient import saveDf

def runForStock(stockId):
    refreshTable('dwd','dwd_ts_stock_daily')
    sql = "SELECT stock_id, trade_date as `date`, open,close,low,high from dwd_ts_stock_daily where stock_id = '%s' order by trade_date asc" % (stockId)
    df = getDfFromSql('dwd',sql)
    features = getHistTradeFeatures(df)
    print(len(features))
    print(features)
    model = ChangLun(df,'D','W')
    model.run()
    plot = ChanLunPlot(model)
    plot.setFeatures(features)
    plot.plot()

def run():
    sql = "SELECT distinct stock_id from dwd_ts_stock_daily"
    df = getDfFromSql('dwd',sql)
    stockList = df['stock_id'].to_list()
    for stock in stockList:
        print(stock)
        try:
            runForStock(stock)
        except:
            print('error... skip')

if __name__ == '__main__':
    #run()
    runForStock('002847')
