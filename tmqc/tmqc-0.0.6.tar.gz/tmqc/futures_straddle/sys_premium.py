
####################################
#贴水  做多近期  做空远期
#升水  做空近期  做多远期
#在近期交割日前15个交易日开仓
####################################

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from frame import stock_func
from common import log
from common import basefunc
import math

class class_premium(object):
    def __init__(this, database, inner_database, portfolios):
        this.inner_database = inner_database
        this.database = database
        this.portfolios = portfolios
        this.total_profit = 0

    def query_instrument_price(this, datetime, instrument_id):#获取某个合约某个交易日的收盘价
        sql = "SELECT ClosePrice FROM hq_cffex_k1 where InstrumentID = '%s' and Time=%d" % (instrument_id, datetime)
        this.database.Query(sql)
        ClosePrice = this.database.FetchOne()
        if not ClosePrice: return None
        return ClosePrice[0]/1000.0

    def query_instrument_trade_dates(this, instrument_id):#获取某个合约所有交易日收盘时间
        sql = "SELECT Time FROM hq_cffex_k1 where InstrumentID = '%s' ORDER BY Time"%instrument_id
        this.database.Query(sql)
        recs  = this.database.FetchAll()
        dates = []
        for rec in recs:
            if rec[0]%10000 !=1500: continue
            dates.append(rec[0])
        return dates

    def get_trade_time(this, current_instrumentID):
        dates = this.query_instrument_trade_dates(current_instrumentID)
        open_date = dates[-15] #近期合约收割日前15个交易日开仓
        close_date = dates[-1]
        return open_date, close_date

    def cal_one_instrument_profit(this, instrumentID, open_date, close_date, is_buy = True):
        open = this.query_instrument_price(open_date, instrumentID)
        if open == None:
            dates = this.query_instrument_trade_dates(instrumentID)
            open_date = (dates[0]/10000)*10000+1500
            open = this.query_instrument_price(open_date, instrumentID)
        close_price = this.query_instrument_price(close_date, instrumentID)
        profit = close_price - open
        if not is_buy: profit = -profit
        return profit


    def cal_profit(this):
        for portfolio in this.portfolios:
            current_instrumentID = portfolio['current'][0]
            open_date, close_date = this.get_trade_time(current_instrumentID)

            stock_index_price,_,_ = stock_func.query_stock_close(this.inner_database, portfolio['stock_index'], 20*1000000 + open_date/10000)
            current_instrument_price = this.query_instrument_price(open_date, current_instrumentID)
            #if math.fabs(current_instrument_price - stock_index_price)<50: continue
            profit = 0
            #贴水
            profit += portfolio['end_price'] - current_instrument_price

            future_open_price = this.query_instrument_price(open_date, portfolio['future'][0])
            if future_open_price == None:
                dates = this.query_instrument_trade_dates(portfolio['future'][0])
                open_date = (dates[0]/10000)*10000+1500
                future_open_price = this.query_instrument_price(open_date, portfolio['future'][0])
            future_close_price = this.query_instrument_price(close_date, portfolio['future'][0])
            profit += future_open_price - future_close_price
            if current_instrument_price > stock_index_price: #升水
                profit = -profit
            this.total_profit += profit
            #print("%s\t%d\t%d\t%.2f"%(portfolio['current'][:6], open_date, close_date, profit))
            #print("%s\t%.2f"%(current_instrumentID[2:6], profit))
            future_stock_index_price,_,_ = stock_func.query_stock_close(this.inner_database, portfolio['stock_index'], 20*1000000 + close_date/10000)
            log.WriteLog('premium', "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f"%(current_instrumentID[2:6], current_instrument_price -stock_index_price, future_open_price -stock_index_price,portfolio['end_price'] - future_stock_index_price, future_close_price - future_stock_index_price,  profit, this.total_profit))

    def draw_curve(this):
        for portfolio in this.portfolios:
            current_instrumentID = portfolio['current'][0]
            future_instrumentID = portfolio['future'][0]
            dates = this.query_instrument_trade_dates(current_instrumentID)
            log.WriteLog(current_instrumentID[2:6],"%s\t%s\t%s\t%s"%(" ","近期", "远期","股指"))
            for date in dates:
                current_instrument_price = this.query_instrument_price(date, current_instrumentID)
                future_instrument_price = this.query_instrument_price(date, future_instrumentID)
                if future_instrument_price == None:future_instrument_price = this.query_instrument_price((date/10000)*10000+1457, future_instrumentID)
                if future_instrument_price == None:future_instrument_price = this.query_instrument_price((date/10000)*10000+1458, future_instrumentID)
                if future_instrument_price == None:future_instrument_price = this.query_instrument_price((date/10000)*10000+1459, future_instrumentID)
                if future_instrument_price == None:future_instrument_price = this.query_instrument_price(date+1, future_instrumentID)
                if future_instrument_price == None:future_instrument_price = this.query_instrument_price(date+2, future_instrumentID)
                if future_instrument_price == None:future_instrument_price = this.query_instrument_price(date+3, future_instrumentID)
                if future_instrument_price == None:future_instrument_price = this.query_instrument_price(date+4, future_instrumentID)
                stock_index_price,_,_ = stock_func.query_stock_close(this.inner_database, portfolio['stock_index'], 20*1000000 + date/10000)
                if future_instrument_price == None:future_instrument_price =0
                log.WriteLog(current_instrumentID[2:6],"%d\t%.2f\t%.2f\t%.2f"%(date/10000, current_instrument_price,future_instrument_price,stock_index_price))








if __name__ == '__main__':
    db_info = {
        'host' 		: '183.131.76.91',
	    'user' 		: 'root',
        'password' 	: 'P)O(I*U&Y^',
        'db' 		: 'stock',
        'port'      : 3308,
        'charset'   :   'utf8'
    }
    datebase = basefunc.create_database(db_info)
    inner_database = basefunc.create_database()

    portfolios = [

                  #{'current':['IH1505'], 'future':[ 'IH1509'], 'end_price':3072.81, 'stock_index':'SH000016'},
                  #{'current':['IH1506'], 'future':[ 'IH1509'], 'end_price':2990.24, 'stock_index':'SH000016'},
                  #{'current':['IH1507'], 'future':[ 'IH1512'], 'end_price':2792.24, 'stock_index':'SH000016'},
                  #{'current':['IH1508'], 'future':[ 'IH1512'], 'end_price':2300.66, 'stock_index':'SH000016'},

                  #{'current':['IC1505'], 'future':[ 'IC1509'], 'end_price':8755.31, 'stock_index':'SH000905'},
                  #{'current':['IC1506'], 'future':[ 'IC1509'], 'end_price':10206.70, 'stock_index':'SH000905'},
                  #{'current':['IC1507'], 'future':[ 'IC1512'], 'end_price':7934.85, 'stock_index':'SH000905'},
                  #{'current':['IC1508'], 'future':[ 'IC1512'], 'end_price':7747.28, 'stock_index':'SH000905'},

                  #{'current':['IF1408'], 'future':['IF1412'], 'end_price':2360.41, 'stock_index':'IF300'},
                  #{'current':['IF1409'], 'future':['IF1412'], 'end_price':2419.41, 'stock_index':'IF300'},
                  #{'current':['IF1410'], 'future':['IF1503'], 'end_price':2438.03, 'stock_index':'IF300'},
                  #{'current':['IF1411'], 'future':['IF1503'], 'end_price':2565.90, 'stock_index':'IF300'},
                  #{'current':['IF1412'], 'future':['IF1503'], 'end_price':3351.58, 'stock_index':'IF300'},
                  #{'current':['IF1501'], 'future':['IF1506'], 'end_price':3641.34, 'stock_index':'IF300'},
                  #{'current':['IF1502'], 'future':['IF1506'], 'end_price':3492.92, 'stock_index':'IF300'},
                  #{'current':['IF1503'], 'future':['IF1506'], 'end_price':3886.79, 'stock_index':'IF300'},
                  #{'current':['IF1504'], 'future':['IF1509'], 'end_price':4599.62, 'stock_index':'IF300'},
                  #{'current':['IF1505'], 'future':['IF1509'], 'end_price':4634.03, 'stock_index':'IF300'},
                  #{'current':['IF1506'], 'future':['IF1509'], 'end_price':4765.10, 'stock_index':'IF300'},
                  #{'current':['IF1507'], 'future':['IF1512'], 'end_price':4124.68, 'stock_index':'IF300'},
                  #{'current':['IF1508'], 'future':['IF1512'], 'end_price':3644.94, 'stock_index':'IF300'},
                  {'current':['IF1510'], 'future':['IF1603'], 'end_price':3493.8, 'stock_index':'IF300'},
                  #{'current':['IF1510'], 'future':['IF1512'], 'end_price':3644.94, 'stock_index':'IF300'},
                 ]
    obj_premium = class_premium(datebase, inner_database, portfolios)
    obj_premium.draw_curve()
    obj_premium.cal_profit()
