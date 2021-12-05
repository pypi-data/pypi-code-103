from influxdb import InfluxDBClient
import QUANTAXIS as QA
import UtilTools.DateUtils as DateUtils
import UtilTools.ProfileUtils as ProfileUtils
from datetime import datetime
from datetime import timedelta

host='192.168.1.153'
port=8086
user = 'admin'
password = 'admin'
dbname = 'stock'
client = InfluxDBClient(host, port, user, password, dbname)

def getTableName(stockId,freq):
    return "stock_%s_%s" % (stockId,freq)

def deleteTable(stockId,freq):
    tableName = getTableName(stockId,freq)
    client.drop_measurement(tableName)

def insertStockData(stockId,stockData,freq):
    tableName = getTableName(stockId,freq)
    points = []
    for data in stockData:
        point = {"measurement": tableName}
        point["tags"] = {"type": data['type']}
        point["time"] = DateUtils.convertTimestampToStr(data['date'])
        point['fields'] = {
            'date': data['date'].timestamp(),
            'open': round(data['open'],2),
            'close':round(data['close'],2),
            'high':round(data['high'],2),
            'low':round(data['low'],2),
            'volume':round(data['volume']),
            'amount':data['amount'],
            'code': stockId
        }
        points.append(point)
    client.write_points(points)

def initStockData(stockId,startDate,endDate,freq):
    stockMin = QA.QA_fetch_stock_min_adv(stockId, startDate, endDate, frequence=freq).to_qfq()
    histData = stockMin.data
    histData['date'] = histData.index.levels[0]
    stockData = histData.to_dict('records')
    points = []
    tableName = getTableName(stockId,freq)
    for data in stockData:
        point = {"measurement": tableName}
        point["tags"] = {"type": data['type']}
        point["time"] = DateUtils.convertTimestampToStr(data['date'])
        point['fields'] = {
            'date': data['date'].timestamp()  - 28800,
            'open': round(data['open'],2),
            'close':round(data['close'],2),
            'high':round(data['high'],2),
            'low':round(data['low'],2),
            'volume':round(data['volume']),
            'amount':data['amount']

        }
        points.append(point)
    client.write_points(points)

def getStockData(stockId,freq):
    tableName = getTableName(stockId,freq)
    rs = client.query("select * from %s" % (tableName))
    result = list(rs.get_points(measurement=tableName))
    for data in result:
        data['date'] = datetime.fromtimestamp(data['date'])
    return result

def getStockDataFromDate(stockId,freq,startDate,endDate):
    tableName = getTableName(stockId,freq)
    rs = client.query("select * from %s where time >= '%s' and time <= '%s'" % (tableName,startDate,endDate))
    result = list(rs.get_points(measurement=tableName))
    for data in result:
        data['date'] = datetime.fromtimestamp(data['date'])
    return result

def getLastDatetime(stockId,freq):
    tableName = getTableName(stockId,freq)
    rs = client.query("select max(date) as date from %s" % (tableName))
    result = list(rs.get_points(measurement=tableName))
    date = datetime.fromtimestamp(result[0]['date'])
    print(date)
    return date

def deleteData(stockId,freq,startDate):
    tableName = getTableName(stockId,freq)
    rs = client.query("delete from %s where time > '%s'" % (tableName,startDate))

def runTest():
    stockId = '000001'
    startDate = '2018-03-26'
    endDate = '2019-03-26'
    freq = '5m'
    #saveStockData(stockId,startDate,endDate,freq)
    #dataList = getStockData(stockId,freq)
    getLastDatetime(stockId,freq)

if __name__ == '__main__':
    deleteData('000001','5m')
