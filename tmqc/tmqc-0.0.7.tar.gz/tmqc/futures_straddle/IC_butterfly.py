
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from common import basefunc
from common import log
from frame import stock_func

def query_instrument_price(database, datetime, instrument_id, table_name):
    sql = "SELECT ClosePrice FROM %s where InstrumentID = '%s' and Time=%d" % (table_name, instrument_id, datetime)
    database.Query(sql)
    ClosePrice = database.FetchOne()
    if not ClosePrice: return None
    return ClosePrice[0]/1000.0


class class_IC_butterfly(object):
    def __init__(this, database, inner_database, config, table_name):
        this.inner_database = inner_database
        this.database = database
        this.config = config
        this.table = table_name
        this.dic_price = {}

    def get_contract_price(this, portfolio, contract_id, datetime):
        key="%s-%d"%(contract_id, datetime)
        if key in this.dic_price:this.dic_price[key]
        price = None
        if contract_id == portfolio['end_contract'] and  datetime == portfolio['end_time']:
            price = portfolio['end_price']
        else:
            price = query_instrument_price(this.database, datetime, contract_id, this.table)
        this.dic_price[key] = price
        return price

    def get_stock_index_price(this, portfolio):
        stock_index = portfolio['stock_index']
        beg_time = portfolio['beg_time']
        datetime = 20*1000000 + beg_time/10000
        close,_,_ = stock_func.query_stock_close(this.inner_database, stock_index, datetime)
        return close

    def get_premiums_discounts(this, portfolio):#计算升贴水
        stock_index = this.get_stock_index_price(portfolio)

        contract_id = portfolio['end_contract']
        datetime = portfolio['beg_time']
        contract_price = this.get_contract_price(portfolio, contract_id, datetime)
        return contract_price - stock_index

    #计算一份合约的收益
    def cal_one_contract_profit(this, portfolio, contract):
        number = 0
        if contract in portfolio['bull']: number = portfolio['bull_num']
        if contract in portfolio['bear']: number = portfolio['bear_num']
        curent_price = this.get_contract_price(portfolio, contract, portfolio['beg_time'])
        future_price = this.get_contract_price(portfolio, contract, portfolio['end_time'])
        profit = (future_price - curent_price)*300*number
        if contract in portfolio['bear']:
            profit = -profit
        return profit

    #计算一个套利组合的收益
    def cal_portfolio_profit(this, portfolio):
        profit = 0
        for contract in (portfolio['bull'] + portfolio['bear']):
            profit += this.cal_one_contract_profit(portfolio, contract)
        return profit


    def get_portfolio_cost(this, portfolio):
        max_cost = 0
        datetimes = [portfolio['beg_time'], portfolio['end_time']]
        for datetime in datetimes:
            cost = 0
            for contract_id in (portfolio['bull'] + portfolio['bear']):
                number = portfolio['bull_num']
                if contract_id in portfolio['bear']: number = portfolio['bear_num']
                price = this.get_contract_price(portfolio, contract_id, datetime)
                cost += price*300*number*0.12
            if cost >max_cost: max_cost = cost
        return max_cost


    def print_result(this):
        for portfolio in config:
            profit = this.cal_portfolio_profit(portfolio)
            cost = this.get_portfolio_cost(portfolio)
            return_rate = profit/float(cost)
            premiums_discounts = this.get_premiums_discounts(portfolio)
            str =  "%s\tprofit:\t%.2f\tcost:\t%0.2f\treturn_rate:\t%0.2f\t%0.2f\t%s"%(portfolio, profit, cost, return_rate, premiums_discounts,  portfolio['is_buy'])
            log.WriteLog('IC_butterfly', str)



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
    
    config = [
              {'bull':['IF1506','IF1509'], 'bear':['IF1507'], 'bear_num':2,'bull_num':1, 'beg_time':1506011500, 'end_time':1506191500, 'end_contract':'IF1506', 'end_price':4765.10, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1506','IF1512'], 'bear':['IF1507'], 'bear_num':2,'bull_num':1, 'beg_time':1506011500, 'end_time':1506191500, 'end_contract':'IF1506', 'end_price':4765.10, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1506','IF1512'], 'bear':['IF1509'], 'bear_num':2,'bull_num':1, 'beg_time':1506011500, 'end_time':1506191500, 'end_contract':'IF1506', 'end_price':4765.10, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1506','IF1509'], 'bull':['IF1507'], 'bear_num':1,'bull_num':2, 'beg_time':1506011500, 'end_time':1506191500, 'end_contract':'IF1506', 'end_price':4765.10, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1506','IF1512'], 'bull':['IF1507'], 'bear_num':1,'bull_num':2, 'beg_time':1506011500, 'end_time':1506191500, 'end_contract':'IF1506', 'end_price':4765.10, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1506','IF1512'], 'bull':['IF1509'], 'bear_num':1,'bull_num':2, 'beg_time':1506011500, 'end_time':1506191500, 'end_contract':'IF1506', 'end_price':4765.10, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1505','IF1509'], 'bear':['IF1506'], 'bear_num':2,'bull_num':1, 'beg_time':1504271500, 'end_time':1505151500, 'end_contract':'IF1505', 'end_price':4634.03, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1505','IF1512'], 'bear':['IF1506'], 'bear_num':2,'bull_num':1, 'beg_time':1504271500, 'end_time':1505151500, 'end_contract':'IF1505', 'end_price':4634.03, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1505','IF1512'], 'bear':['IF1509'], 'bear_num':2,'bull_num':1, 'beg_time':1504271500, 'end_time':1505151500, 'end_contract':'IF1505', 'end_price':4634.03, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1505','IF1509'], 'bull':['IF1506'], 'bear_num':1,'bull_num':2, 'beg_time':1504271500, 'end_time':1505151500, 'end_contract':'IF1505', 'end_price':4634.03, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1505','IF1512'], 'bull':['IF1506'], 'bear_num':1,'bull_num':2, 'beg_time':1504271500, 'end_time':1505151500, 'end_contract':'IF1505', 'end_price':4634.03, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1505','IF1512'], 'bull':['IF1509'], 'bear_num':1,'bull_num':2, 'beg_time':1504271500, 'end_time':1505151500, 'end_contract':'IF1505', 'end_price':4634.03, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1504','IF1506'], 'bear':['IF1505'], 'bear_num':2,'bull_num':1, 'beg_time':1503301500, 'end_time':1504171500, 'end_contract':'IF1504', 'end_price':4599.62, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1504','IF1509'], 'bear':['IF1505'], 'bear_num':2,'bull_num':1, 'beg_time':1503301500, 'end_time':1504171500, 'end_contract':'IF1504', 'end_price':4599.62, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1504','IF1509'], 'bear':['IF1506'], 'bear_num':2,'bull_num':1, 'beg_time':1503301500, 'end_time':1504171500, 'end_contract':'IF1504', 'end_price':4599.62, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1504','IF1506'], 'bull':['IF1505'], 'bear_num':1,'bull_num':2, 'beg_time':1503301500, 'end_time':1504171500, 'end_contract':'IF1504', 'end_price':4599.62, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1504','IF1509'], 'bull':['IF1505'], 'bear_num':1,'bull_num':2, 'beg_time':1503301500, 'end_time':1504171500, 'end_contract':'IF1504', 'end_price':4599.62, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1504','IF1509'], 'bull':['IF1506'], 'bear_num':1,'bull_num':2, 'beg_time':1503301500, 'end_time':1504171500, 'end_contract':'IF1504', 'end_price':4599.62, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1503','IF1506'], 'bear':['IF1504'], 'bear_num':2,'bull_num':1, 'beg_time':1503021500, 'end_time':1503201500, 'end_contract':'IF1503', 'end_price':3886.79, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1503','IF1509'], 'bear':['IF1504'], 'bear_num':2,'bull_num':1, 'beg_time':1503021500, 'end_time':1503201500, 'end_contract':'IF1503', 'end_price':3886.79, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1503','IF1509'], 'bear':['IF1506'], 'bear_num':2,'bull_num':1, 'beg_time':1503021500, 'end_time':1503201500, 'end_contract':'IF1503', 'end_price':3886.79, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1503','IF1506'], 'bull':['IF1504'], 'bear_num':1,'bull_num':2, 'beg_time':1503021500, 'end_time':1503201500, 'end_contract':'IF1503', 'end_price':3886.79, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1503','IF1509'], 'bull':['IF1504'], 'bear_num':1,'bull_num':2, 'beg_time':1503021500, 'end_time':1503201500, 'end_contract':'IF1503', 'end_price':3886.79, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1503','IF1509'], 'bull':['IF1506'], 'bear_num':1,'bull_num':2, 'beg_time':1503021500, 'end_time':1503201500, 'end_contract':'IF1503', 'end_price':3886.79, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1502','IF1506'], 'bear':['IF1503'], 'bear_num':2,'bull_num':1, 'beg_time':1502051500, 'end_time':1502251500, 'end_contract':'IF1502', 'end_price':3492.92, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1502','IF1509'], 'bear':['IF1503'], 'bear_num':2,'bull_num':1, 'beg_time':1502051500, 'end_time':1502251500, 'end_contract':'IF1502', 'end_price':3492.92, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1502','IF1509'], 'bear':['IF1506'], 'bear_num':2,'bull_num':1, 'beg_time':1502051500, 'end_time':1502251500, 'end_contract':'IF1502', 'end_price':3492.92, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1502','IF1506'], 'bull':['IF1503'], 'bear_num':1,'bull_num':2, 'beg_time':1502051500, 'end_time':1502251500, 'end_contract':'IF1502', 'end_price':3492.92, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1502','IF1509'], 'bull':['IF1503'], 'bear_num':1,'bull_num':2, 'beg_time':1502051500, 'end_time':1502251500, 'end_contract':'IF1502', 'end_price':3492.92, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1502','IF1509'], 'bull':['IF1506'], 'bear_num':1,'bull_num':2, 'beg_time':1502051500, 'end_time':1502251500, 'end_contract':'IF1502', 'end_price':3492.92, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1501','IF1503'], 'bear':['IF1502'], 'bear_num':2,'bull_num':1, 'beg_time':1412291500, 'end_time':1501161500, 'end_contract':'IF1501', 'end_price':3641.34, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1501','IF1506'], 'bear':['IF1502'], 'bear_num':2,'bull_num':1, 'beg_time':1412291500, 'end_time':1501161500, 'end_contract':'IF1501', 'end_price':3641.34, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1501','IF1506'], 'bear':['IF1503'], 'bear_num':2,'bull_num':1, 'beg_time':1412291500, 'end_time':1501161500, 'end_contract':'IF1501', 'end_price':3641.34, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1501','IF1503'], 'bull':['IF1502'], 'bear_num':1,'bull_num':2, 'beg_time':1412291500, 'end_time':1501161500, 'end_contract':'IF1501', 'end_price':3641.34, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1501','IF1506'], 'bull':['IF1502'], 'bear_num':1,'bull_num':2, 'beg_time':1412291500, 'end_time':1501161500, 'end_contract':'IF1501', 'end_price':3641.34, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1501','IF1506'], 'bull':['IF1503'], 'bear_num':1,'bull_num':2, 'beg_time':1412291500, 'end_time':1501161500, 'end_contract':'IF1501', 'end_price':3641.34, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1412','IF1503'], 'bear':['IF1501'], 'bear_num':2,'bull_num':1, 'beg_time':1412011500, 'end_time':1412191500, 'end_contract':'IF1412', 'end_price':3351.58, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1412','IF1506'], 'bear':['IF1501'], 'bear_num':2,'bull_num':1, 'beg_time':1412011500, 'end_time':1412191500, 'end_contract':'IF1412', 'end_price':3351.58, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1412','IF1506'], 'bear':['IF1503'], 'bear_num':2,'bull_num':1, 'beg_time':1412011500, 'end_time':1412191500, 'end_contract':'IF1412', 'end_price':3351.58, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1412','IF1503'], 'bull':['IF1501'], 'bear_num':1,'bull_num':2, 'beg_time':1412011500, 'end_time':1412191500, 'end_contract':'IF1412', 'end_price':3351.58, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1412','IF1506'], 'bull':['IF1501'], 'bear_num':1,'bull_num':2, 'beg_time':1412011500, 'end_time':1412191500, 'end_contract':'IF1412', 'end_price':3351.58, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1412','IF1506'], 'bull':['IF1503'], 'bear_num':1,'bull_num':2, 'beg_time':1412011500, 'end_time':1412191500, 'end_contract':'IF1412', 'end_price':3351.58, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1411','IF1503'], 'bear':['IF1412'], 'bear_num':2,'bull_num':1, 'beg_time':1411031500, 'end_time':1411211500, 'end_contract':'IF1411', 'end_price':2565.90, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1411','IF1506'], 'bear':['IF1412'], 'bear_num':2,'bull_num':1, 'beg_time':1411031500, 'end_time':1411211500, 'end_contract':'IF1411', 'end_price':2565.90, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1411','IF1506'], 'bear':['IF1503'], 'bear_num':2,'bull_num':1, 'beg_time':1411031500, 'end_time':1411211500, 'end_contract':'IF1411', 'end_price':2565.90, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1411','IF1503'], 'bull':['IF1412'], 'bear_num':1,'bull_num':2, 'beg_time':1411031500, 'end_time':1411211500, 'end_contract':'IF1411', 'end_price':2565.90, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1411','IF1506'], 'bull':['IF1412'], 'bear_num':1,'bull_num':2, 'beg_time':1411031500, 'end_time':1411211500, 'end_contract':'IF1411', 'end_price':2565.90, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1411','IF1506'], 'bull':['IF1503'], 'bear_num':1,'bull_num':2, 'beg_time':1411031500, 'end_time':1411211500, 'end_contract':'IF1411', 'end_price':2565.90, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1410','IF1412'], 'bear':['IF1411'], 'bear_num':2,'bull_num':1, 'beg_time':1409291500, 'end_time':1410171500, 'end_contract':'IF1410', 'end_price':2438.03, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1410','IF1503'], 'bear':['IF1411'], 'bear_num':2,'bull_num':1, 'beg_time':1409291500, 'end_time':1410171500, 'end_contract':'IF1410', 'end_price':2438.03, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1410','IF1503'], 'bear':['IF1412'], 'bear_num':2,'bull_num':1, 'beg_time':1409291500, 'end_time':1410171500, 'end_contract':'IF1410', 'end_price':2438.03, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1410','IF1412'], 'bull':['IF1411'], 'bear_num':1,'bull_num':2, 'beg_time':1409291500, 'end_time':1410171500, 'end_contract':'IF1410', 'end_price':2438.03, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1410','IF1503'], 'bull':['IF1411'], 'bear_num':1,'bull_num':2, 'beg_time':1409291500, 'end_time':1410171500, 'end_contract':'IF1410', 'end_price':2438.03, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1410','IF1503'], 'bull':['IF1412'], 'bear_num':1,'bull_num':2, 'beg_time':1409291500, 'end_time':1410171500, 'end_contract':'IF1410', 'end_price':2438.03, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1409','IF1412'], 'bear':['IF1410'], 'bear_num':2,'bull_num':1, 'beg_time':1409011500, 'end_time':1409191500, 'end_contract':'IF1409', 'end_price':2419.41, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1409','IF1503'], 'bear':['IF1410'], 'bear_num':2,'bull_num':1, 'beg_time':1409011500, 'end_time':1409191500, 'end_contract':'IF1409', 'end_price':2419.41, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1409','IF1503'], 'bear':['IF1412'], 'bear_num':2,'bull_num':1, 'beg_time':1409011500, 'end_time':1409191500, 'end_contract':'IF1409', 'end_price':2419.41, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1409','IF1412'], 'bull':['IF1410'], 'bear_num':1,'bull_num':2, 'beg_time':1409011500, 'end_time':1409191500, 'end_contract':'IF1409', 'end_price':2419.41, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1409','IF1503'], 'bull':['IF1410'], 'bear_num':1,'bull_num':2, 'beg_time':1409011500, 'end_time':1409191500, 'end_contract':'IF1409', 'end_price':2419.41, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1409','IF1503'], 'bull':['IF1412'], 'bear_num':1,'bull_num':2, 'beg_time':1409011500, 'end_time':1409191500, 'end_contract':'IF1409', 'end_price':2419.41, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1408','IF1412'], 'bear':['IF1409'], 'bear_num':2,'bull_num':1, 'beg_time':1407281500, 'end_time':1408151500, 'end_contract':'IF1408', 'end_price':2360.41, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1408','IF1503'], 'bear':['IF1409'], 'bear_num':2,'bull_num':1, 'beg_time':1407281500, 'end_time':1408151500, 'end_contract':'IF1408', 'end_price':2360.41, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1408','IF1503'], 'bear':['IF1412'], 'bear_num':2,'bull_num':1, 'beg_time':1407281500, 'end_time':1408151500, 'end_contract':'IF1408', 'end_price':2360.41, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1408','IF1412'], 'bull':['IF1409'], 'bear_num':1,'bull_num':2, 'beg_time':1407281500, 'end_time':1408151500, 'end_contract':'IF1408', 'end_price':2360.41, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1408','IF1503'], 'bull':['IF1409'], 'bear_num':1,'bull_num':2, 'beg_time':1407281500, 'end_time':1408151500, 'end_contract':'IF1408', 'end_price':2360.41, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1408','IF1503'], 'bull':['IF1412'], 'bear_num':1,'bull_num':2, 'beg_time':1407281500, 'end_time':1408151500, 'end_contract':'IF1408', 'end_price':2360.41, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1407','IF1409'], 'bear':['IF1408'], 'bear_num':2,'bull_num':1, 'beg_time':1406301500, 'end_time':1407181500, 'end_contract':'IF1407', 'end_price':2167.21, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1407','IF1412'], 'bear':['IF1408'], 'bear_num':2,'bull_num':1, 'beg_time':1406301500, 'end_time':1407181500, 'end_contract':'IF1407', 'end_price':2167.21, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1407','IF1412'], 'bear':['IF1409'], 'bear_num':2,'bull_num':1, 'beg_time':1406301500, 'end_time':1407181500, 'end_contract':'IF1407', 'end_price':2167.21, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1407','IF1409'], 'bull':['IF1408'], 'bear_num':1,'bull_num':2, 'beg_time':1406301500, 'end_time':1407181500, 'end_contract':'IF1407', 'end_price':2167.21, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1407','IF1412'], 'bull':['IF1408'], 'bear_num':1,'bull_num':2, 'beg_time':1406301500, 'end_time':1407181500, 'end_contract':'IF1407', 'end_price':2167.21, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1407','IF1412'], 'bull':['IF1409'], 'bear_num':1,'bull_num':2, 'beg_time':1406301500, 'end_time':1407181500, 'end_contract':'IF1407', 'end_price':2167.21, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1406','IF1409'], 'bear':['IF1407'], 'bear_num':2,'bull_num':1, 'beg_time':1406031500, 'end_time':1406201500, 'end_contract':'IF1406', 'end_price':2129.81, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1406','IF1412'], 'bear':['IF1407'], 'bear_num':2,'bull_num':1, 'beg_time':1406031500, 'end_time':1406201500, 'end_contract':'IF1406', 'end_price':2129.81, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1406','IF1412'], 'bear':['IF1409'], 'bear_num':2,'bull_num':1, 'beg_time':1406031500, 'end_time':1406201500, 'end_contract':'IF1406', 'end_price':2129.81, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1406','IF1409'], 'bull':['IF1407'], 'bear_num':1,'bull_num':2, 'beg_time':1406031500, 'end_time':1406201500, 'end_contract':'IF1406', 'end_price':2129.81, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1406','IF1412'], 'bull':['IF1407'], 'bear_num':1,'bull_num':2, 'beg_time':1406031500, 'end_time':1406201500, 'end_contract':'IF1406', 'end_price':2129.81, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1406','IF1412'], 'bull':['IF1409'], 'bear_num':1,'bull_num':2, 'beg_time':1406031500, 'end_time':1406201500, 'end_contract':'IF1406', 'end_price':2129.81, 'stock_index':'IF300', 'is_buy':False},


              {'bull':['IF1405','IF1409'], 'bear':['IF1406'], 'bear_num':2,'bull_num':1, 'beg_time':1404281500, 'end_time':1405161500, 'end_contract':'IF1405', 'end_price':2141.99, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1405','IF1412'], 'bear':['IF1406'], 'bear_num':2,'bull_num':1, 'beg_time':1404281500, 'end_time':1405161500, 'end_contract':'IF1405', 'end_price':2141.99, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1405','IF1412'], 'bear':['IF1409'], 'bear_num':2,'bull_num':1, 'beg_time':1404281500, 'end_time':1405161500, 'end_contract':'IF1405', 'end_price':2141.99, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1405','IF1409'], 'bull':['IF1406'], 'bear_num':1,'bull_num':2, 'beg_time':1404281500, 'end_time':1405161500, 'end_contract':'IF1405', 'end_price':2141.99, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1405','IF1412'], 'bull':['IF1406'], 'bear_num':1,'bull_num':2, 'beg_time':1404281500, 'end_time':1405161500, 'end_contract':'IF1405', 'end_price':2141.99, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1405','IF1412'], 'bull':['IF1409'], 'bear_num':1,'bull_num':2, 'beg_time':1404281500, 'end_time':1405161500, 'end_contract':'IF1405', 'end_price':2141.99, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1404','IF1406'], 'bear':['IF1405'], 'bear_num':2,'bull_num':1, 'beg_time':1403311500, 'end_time':1404181500, 'end_contract':'IF1404', 'end_price':2220.74, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1404','IF1409'], 'bear':['IF1405'], 'bear_num':2,'bull_num':1, 'beg_time':1403311500, 'end_time':1404181500, 'end_contract':'IF1404', 'end_price':2220.74, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1404','IF1409'], 'bear':['IF1406'], 'bear_num':2,'bull_num':1, 'beg_time':1403311500, 'end_time':1404181500, 'end_contract':'IF1404', 'end_price':2220.74, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1404','IF1406'], 'bull':['IF1405'], 'bear_num':1,'bull_num':2, 'beg_time':1403311500, 'end_time':1404181500, 'end_contract':'IF1404', 'end_price':2220.74, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1404','IF1409'], 'bull':['IF1405'], 'bear_num':1,'bull_num':2, 'beg_time':1403311500, 'end_time':1404181500, 'end_contract':'IF1404', 'end_price':2220.74, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1404','IF1409'], 'bull':['IF1406'], 'bear_num':1,'bull_num':2, 'beg_time':1403311500, 'end_time':1404181500, 'end_contract':'IF1404', 'end_price':2220.74, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1403','IF1406'], 'bear':['IF1404'], 'bear_num':2,'bull_num':1, 'beg_time':1403031500, 'end_time':1403211500, 'end_contract':'IF1403', 'end_price':2143.10, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1403','IF1409'], 'bear':['IF1404'], 'bear_num':2,'bull_num':1, 'beg_time':1403031500, 'end_time':1403211500, 'end_contract':'IF1403', 'end_price':2143.10, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1403','IF1409'], 'bear':['IF1406'], 'bear_num':2,'bull_num':1, 'beg_time':1403031500, 'end_time':1403211500, 'end_contract':'IF1403', 'end_price':2143.10, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1403','IF1406'], 'bull':['IF1404'], 'bear_num':1,'bull_num':2, 'beg_time':1403031500, 'end_time':1403211500, 'end_contract':'IF1403', 'end_price':2143.10, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1403','IF1409'], 'bull':['IF1404'], 'bear_num':1,'bull_num':2, 'beg_time':1403031500, 'end_time':1403211500, 'end_contract':'IF1403', 'end_price':2143.10, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1403','IF1409'], 'bull':['IF1406'], 'bear_num':1,'bull_num':2, 'beg_time':1403031500, 'end_time':1403211500, 'end_contract':'IF1403', 'end_price':2143.10, 'stock_index':'IF300', 'is_buy':False},

              {'bull':['IF1402','IF1406'], 'bear':['IF1403'], 'bear_num':2,'bull_num':1, 'beg_time':1401301500, 'end_time':1402211500, 'end_contract':'IF1402', 'end_price':2260.92, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1402','IF1409'], 'bear':['IF1403'], 'bear_num':2,'bull_num':1, 'beg_time':1401301500, 'end_time':1402211500, 'end_contract':'IF1402', 'end_price':2260.92, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1402','IF1409'], 'bear':['IF1406'], 'bear_num':2,'bull_num':1, 'beg_time':1401301500, 'end_time':1402211500, 'end_contract':'IF1402', 'end_price':2260.92, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1402','IF1406'], 'bull':['IF1403'], 'bear_num':1,'bull_num':2, 'beg_time':1401301500, 'end_time':1402211500, 'end_contract':'IF1402', 'end_price':2260.92, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1402','IF1409'], 'bull':['IF1403'], 'bear_num':1,'bull_num':2, 'beg_time':1401301500, 'end_time':1402211500, 'end_contract':'IF1402', 'end_price':2260.92, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1402','IF1409'], 'bull':['IF1406'], 'bear_num':1,'bull_num':2, 'beg_time':1401301500, 'end_time':1402211500, 'end_contract':'IF1402', 'end_price':2260.92, 'stock_index':'IF300', 'is_buy':False},


              {'bull':['IF1401','IF1403'], 'bear':['IF1402'], 'bear_num':2,'bull_num':1, 'beg_time':1312301500, 'end_time':1401171500, 'end_contract':'IF1401', 'end_price':2182.86, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1401','IF1406'], 'bear':['IF1402'], 'bear_num':2,'bull_num':1, 'beg_time':1312301500, 'end_time':1401171500, 'end_contract':'IF1401', 'end_price':2182.86, 'stock_index':'IF300', 'is_buy':True},
              {'bull':['IF1401','IF1406'], 'bear':['IF1403'], 'bear_num':2,'bull_num':1, 'beg_time':1312301500, 'end_time':1401171500, 'end_contract':'IF1401', 'end_price':2182.86, 'stock_index':'IF300', 'is_buy':True},
              {'bear':['IF1401','IF1403'], 'bull':['IF1402'], 'bear_num':1,'bull_num':2, 'beg_time':1312301500, 'end_time':1401171500, 'end_contract':'IF1401', 'end_price':2182.86, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1401','IF1406'], 'bull':['IF1402'], 'bear_num':1,'bull_num':2, 'beg_time':1312301500, 'end_time':1401171500, 'end_contract':'IF1401', 'end_price':2182.86, 'stock_index':'IF300', 'is_buy':False},
              {'bear':['IF1401','IF1406'], 'bull':['IF1403'], 'bear_num':1,'bull_num':2, 'beg_time':1312301500, 'end_time':1401171500, 'end_contract':'IF1401', 'end_price':2182.86, 'stock_index':'IF300', 'is_buy':False},
              #{'bull':['IC1506','IC1509'], 'bear':['IC1507'], 'bear_num':2,'bull_num':1, 'beg_time':1506011500, 'end_time':1506191500, 'end_contract':'IC1506', 'end_price':10206.7, 'is_buy':True},
              #{'bull':['IC1506','IC1512'], 'bear':['IC1507'], 'bear_num':2,'bull_num':1, 'beg_time':1506011500, 'end_time':1506191500, 'end_contract':'IC1506', 'end_price':10206.7, 'is_buy':True},
              #{'bull':['IC1506','IC1512'], 'bear':['IC1509'], 'bear_num':2,'bull_num':1, 'beg_time':1506011500, 'end_time':1506191500, 'end_contract':'IC1506', 'end_price':10206.7, 'is_buy':True},
             ]
    IC_butterfly = class_IC_butterfly(datebase, inner_database, config, 'hq_cffex_k1')
    IC_butterfly.print_result()
