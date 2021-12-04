import pandas as pd
from typing import List

def json_write_dataframe_list(dataframe_list : List[pd.DataFrame]):
    json_dataframe_list = []
    for dataframe in dataframe_list:
        json_dataframe_list.append(json_write_dataframe(dataframe))
    return json_dataframe_list

def json_read_dataframe_list(json_dataframe_list) -> List[pd.DataFrame]:
    dataframe_list = []
    for json_dataframe in json_dataframe_list:
        dataframe_list.append(json_read_dataframe(json_dataframe))
    return dataframe_list

def json_write_dataframe(dataframe : pd.DataFrame):
    return dataframe.to_json(orient='table')

def json_read_dataframe(json_dataframe) -> pd.DataFrame:
    return pd.read_json(json_dataframe, orient='table')

#read in list of objects and returns pandas dataframe
def get_df_obj_list(list_obj):
    return pd.DataFrame.from_records([o.__dict__ for o in list_obj])