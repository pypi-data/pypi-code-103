# -*- coding: utf-8 -*-
import grpc
import sys
sys.path.append("./")
from tradeTools import indexData_pb2,indexData_pb2_grpc
from google.protobuf.json_format import MessageToJson
import json
import better_exceptions
import time
import code
import os
from tradeTools import Decorator
from tradeTools import helpers
import pandas as pd
better_exceptions.hook()

HOST = "localhost"
# HOST = "113.31.119.58"
PORT = 50052

def getIndexSymbols(dateTime = 20100118,indexID = "000300",):
    while 1:
        try:
            with grpc.insecure_channel(f"{HOST}:{PORT}") as channel:
                stub = indexData_pb2_grpc.indexDataStub(channel)

                print("=====【rpc】 getSymbols==========")
                sReq = json.dumps({
                    "indexID":indexID, "dateTime":int(dateTime)})
                response = stub.getSymbols(indexData_pb2.JSONRequest(sReq=sReq))
                jsonRsp = MessageToJson(response)
                jsonRsp = json.loads(jsonRsp)
                return jsonRsp["symbol"]
        except Exception as e:
            print(e)
            time.sleep(3)

class IndexData:
    # todo:akshare 数据不全
    def __init__(self):
        self.indexDfs = {}

    def load(self,indexID = "000300"):
        _realPathFile  = (os.path.realpath(__file__))
        _path = os.path.split(_realPathFile)[0]
        fileName = os.sep.join([_path,r"data", "IndexCons", f"{indexID}指数成分股数据.xlsx"])  #
        df = pd.read_excel(fileName, sheet_name="Sheet", index_col=0,engine="openpyxl")
        df.sort_index(ascending=True, inplace=True)
        df['date'] = pd.to_datetime(df.index, format='%Y-%m-%d')
        df.set_index('date', inplace=True)
        return df

    def getSymbols(self, dateTime, indexSymbol="SH.000300"):
        if indexSymbol not in self.indexDfs:
            self.indexDfs[indexSymbol] = self.load(indexID=indexSymbol[-6:])
        indexDF = self.indexDfs[indexSymbol]
        df = indexDF.iloc[indexDF.index <= str(dateTime)]
        symbols = []
        for index, row in df.iterrows():
            symbol = row["代码"][-2:] + "." + row["代码"][:6]
            addOrDel = row[r"纳入/剔除"]
            if addOrDel == "纳入":
                symbols.append(symbol)
            elif addOrDel == "剔除":
                symbols.remove(symbol)
            else:
                print(f"纳入/剔除 列的值错误 #{addOrDel}#")
        symbols.sort()
        return symbols
    # @Decorator.loadData(path="data")
    # def qryIndexStockCons(self,symbol = "SH.000300"):
    #     import akshare as ak
    #     symbol = symbol[:2].lower()+symbol[-6:]
    #     index_stock_info_df = ak.index_stock_hist(index=symbol)
    #     return index_stock_info_df
    #
    # def getIndexCons(self,dateTime,symbol = "SH.000300"):
    #     cons = self.qryIndexStockCons(symbol = symbol)
    #     cons["tmp"] = cons["in_date"].astype(str)+cons["stock_code"].astype(str)
    #     cons = cons.drop_duplicates('tmp', 'first', ignore_index=True)
    #     cons["in_date"] = pd.to_datetime( cons["in_date"], format='%Y-%m-%d')
    #     cons["out_date"] = pd.to_datetime( cons["out_date"], format='%Y-%m-%d')
    #     into = cons[cons.in_date<=str(dateTime)]["stock_code"].tolist()
    #     print(len(into))
    #     print(into)
    #     ret =[]
    #     for _into in into:
    #         symbol = helpers.code_add_prefix(_into)
    #         ret.append(symbol)
    #     ret.sort()
    #     print(ret)
if __name__ == '__main__':
    # logging.basicConfig()
    # symbols500 = getIndexSymbols()
    # print(symbols500)
    # symbols300 = getIndexSymbols(indexID="000300")
    # print(symbols300)
    # d = list(set(symbols300)&set(symbols500))
    # print(len(d))
    idxData =IndexData()
    # idxData.qryIndexStockCons(symbol = "SH.000300")
    r = idxData.getSymbols(dateTime = 20050408)
    print(len(r))