from UtilTools.impalaUtils import getDfFromSql
from ChangLunLogic.ChangLun import ChangLun
from Plot.ChanLunPlot import ChanLunPlot

if __name__ == '__main__':
    stockId = '002847'
    sql = "SELECT stock_id, trade_date as `date`, open,close,low,high from dwd_ts_stock_daily where stock_id = '%s' order by trade_date asc" % (stockId)
    df = getDfFromSql('dwd',sql)
    df = df[df['date'] <= '20210305']
    model = ChangLun(df,'D','M')
    model.run()
    model.isPenBuyPoint()
    plot = ChanLunPlot(model)
    plot.plot()
    featureDf = model.genFeature()
    print(featureDf)