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
    df = (
        pd.DataFrame(data['Time Series (Daily)'])
        .T.reset_index()
        .rename(columns={'index': 'date'})
    )
    df = df[df['date'] == ds]
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    df.drop('volume', axis=1, inplace=True)
    df.reset_index(drop=True, inplace=True)
    for c in df.columns:
        if c != 'date':
            df[c] = df[c].astype(float)
    df['symbol'] = stock_symbol
    df = df[['symbol', 'date', 'open', 'high', 'low', 'close']]
    df_json = df.to_json()
    return df_json


def stock_data_to_pd(stocks, jsons_dict):
    """Transforms data from dict with jsons into dataframe.

    Attributes
    ----------
        stocks: str
            Symbol of company to get info.
        jsons_dict: Dict[str,json]
            Json data for each company.


    Returns
    -------
        df: DataFrame
            Data in DataFrame formar, ready to be inserted in table.
    """
    dfs = []
    for ticker in stocks:
        stock_df = pd.read_json(
            jsons_dict[ticker],
            orient='index',
        ).T
        stock_df = stock_df[['symbol', 'date', 'open', 'high', 'low', 'close']]
        dfs.append(stock_df)
    df = pd.concat(dfs, axis=0)
    return df
