import json
import time

import pandas as pd
import requests  # type: ignore


def get_stock_data(stock_symbol, ds, base_url, api_key, stock_fn):
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
    return df.to_json()


def stock_data_to_pd(stocks, jsons_dict):
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
