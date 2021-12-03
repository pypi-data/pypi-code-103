"""Functions to work with stock data."""
import json
import time

import pandas as pd
import requests  # type: ignore


def get_stock_data(stock_symbol, ds, base_url, api_key, stock_fn):
    """Gets data from API in json format.

    Attributes
    ----------
        stock_symbol: str
            Symbol of company to get data.
        ds: str
            YYYY-MM-DD format of date to filter data.
        base_url: str
            URL endpoint of the API where data is extracted from.
        api_key: str
            User key in the API.
        stock_fn: str
            Serie of the API to extract.

    Returns
    -------
        df_json: json
            Data to be inserted in table, in json format.
    """
    end_point = (
        f"{base_url}?function={stock_fn}&symbol={stock_symbol}"
        f"&apikey={api_key}&datatype=json"
    )
    print(f"Getting data from {end_point}...")
    r = requests.get(end_point)
    time.sleep(15)  # To avoid api limits
    data = json.loads(r.content)
    data_key = [c for c in data.keys() if c != "Meta Data"][0]
    df = (
        pd.DataFrame(data[data_key])
        .T.reset_index()
        .rename(columns={"index": "date"})
    )
    df = df[df["date"] == ds]
    df.columns = ["date", "open", "high", "low", "close", "volume"]
    df.drop("volume", axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    for c in df.columns:
        if c != "date":
            df[c] = df[c].astype(float)
    df["symbol"] = stock_symbol
    df = df[["symbol", "date", "open", "high", "low", "close"]]
    df_json = df.to_json()
    return df_json


def stock_data_to_pd(jsons_list):
    """Transforms data from dict with jsons into pandas.DataFrame.

    Attributes
    ----------
        jsons_list: List[json]
            Json data for each company.


    Returns
    -------
        df: pandas.DataFrame
            Data in pandas.DataFrame format, ready to be inserted in table.
    """
    dfs = []
    for stock_json in jsons_list:
        stock_df = pd.read_json(stock_json)
        stock_df = stock_df[["symbol", "date", "open", "high", "low", "close"]]
        dfs.append(stock_df)
    df = pd.concat(dfs, axis=0)
    return df
