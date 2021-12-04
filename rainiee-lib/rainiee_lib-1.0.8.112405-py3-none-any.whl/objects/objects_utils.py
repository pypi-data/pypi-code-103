import json

from rainiee_lib.objects.portfolio import portfolio
from rainiee_lib.objects.stocks import stocks, indexs
from typing import List

portfolio_defualt_fields = ["symbol","weights","est_ret","ext"]
def get_fields_json(obj : object, fields : List[str]) -> dict:
    json_output = {}
    for field in fields:
        json_output.update({field: getattr(obj, field)})
    return json_output

def to_json_object_list(object_list : list):
    return [obj.to_json() for obj in object_list]

def from_json_object_list(object_type :str, json_list: List[dict]):
    append_list = []
    for input in json_list:
        instance = get_instance(object_type)
        instance.from_json(input)
        append_list.append(instance)
    return append_list

def from_json_object(object_type: str, json_input : dict):
    instance = get_instance(object_type)
    instance.from_json(json_input)
    return instance

def get_instance(object_type:str):
    if (object_type == "Stock"):
        return stocks.Stock()
    if (object_type == "StockHistory"):
        return stocks.StockHistory()
    if (object_type == "Index"):
        return indexs.Index()
    if (object_type == "IndexHistory"):
        return indexs.IndexHistory()
    if (object_type == "StockHistoryFetcher"):
        return stocks.StockHistoryFetcher()
    if (object_type == "PortfolioEntries"):
        return portfolio.PortfolioEntries()
    if (object_type == "PortfolioParams"):
        return portfolio.PortfolioParams()
    return None

def get_value(obj:object,key:str):
    if isinstance(obj,dict):
        return obj.get(key)
    return getattr(obj,key)

def set_value(self:object,key:str,value:object):
    if isinstance(self,dict):
        self[key] = value
        return
    setattr(self,key,value)


def set_attrs(obj:object,input_dict:dict):
    for key,value in input_dict.items():
        setattr(obj,key,value)