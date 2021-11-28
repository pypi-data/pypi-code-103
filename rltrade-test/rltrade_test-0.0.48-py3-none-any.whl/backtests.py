import pyfolio
import pandas as pd
from copy import deepcopy

from rltrade import config
from rltrade.data import IBKRDownloader, YahooDownloader
from pyfolio import timeseries

def get_daily_return(df,value_col_name="account_value"):
    df = deepcopy(df)
    df['daily_return'] =df[value_col_name].pct_change(1)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date',inplace=True,drop=True)
    df.index = df.index.tz_localize("UTC")
    return pd.Series(df["daily_return"],index=df.index)

def convert_daily_return_to_pyfolio_ts(df):
    strategy_ret = df.copy()
    strategy_ret['date'] = pd.to_datetime(strategy_ret['date'])
    strategy_ret.set_index('date',drop=False,inplace=True)
    strategy_ret.index = strategy_ret.index.tz_localize("UTC")
    del strategy_ret['date']
    return pd.Series(strategy_ret['daily_return'].to_numpy(),index=strategy_ret.index)

def get_baseline(ticker,start,end,mode):
    if mode == 'daily':
        df = IBKRDownloader(start_date=start,
        end_date=end,ticker_list=ticker
        ).fetch_data()
    elif mode == 'min':
        df = IBKRDownloader(start_date=start,
        end_date=end,ticker_list=ticker
        ).fetch_min_data()
    return df

def backtest_stats(df,baseline_start = config.START_TRADE_DATE,
                baseline_end = config.END_DATE,
                baseline_ticker='^DJI',
                value_col_name="account_value",
                mode='daily'):

    if value_col_name == "daily_return":
        df = convert_daily_return_to_pyfolio_ts(df)
    
    if value_col_name == "account_value":
        df = get_daily_return(df,value_col_name=value_col_name)
    
    perf_stats_all = timeseries.perf_stats(
        returns=df,
        turnover_denom="AGB")
    
    baseline_df = get_baseline(ticker=baseline_ticker,start=baseline_start,end=baseline_end,mode=mode)
    baseline_df['date'] = pd.to_datetime(baseline_df['date'],format="%Y-%m-%d")
    # baseline_df = pd.merge(df['date'],perf_stats_all,how='left',on='date')
    baseline_df = baseline_df.fillna(method='ffill').fillna(method='bfill')
    baseline_returns = get_daily_return(baseline_df,value_col_name="close")
    perf_baseline = timeseries.perf_stats(returns=baseline_returns,
                                            turnover_denom='AGB')

    df = pd.concat((perf_stats_all,perf_baseline),axis=1)
    df.columns = ["model","baseline"]
    return df


def backtest_plot(account_value,baseline_start = config.START_TRADE_DATE,
                baseline_end = config.END_DATE,
                baseline_ticker='^DJI',
                value_col_name="account_value",
                mode='daily'):
    df = deepcopy(account_value)
    df['date'] = pd.to_datetime(df['date'])

    if value_col_name == "daily_return":
        test_returns = convert_daily_return_to_pyfolio_ts(df)
    
    if value_col_name == "account_value":
        test_returns = get_daily_return(df,value_col_name=value_col_name)

    baseline_df = get_baseline(ticker=baseline_ticker,start=baseline_start,end=baseline_end,mode=mode)
    baseline_df['date'] = pd.to_datetime(baseline_df['date'],format="%Y-%m-%d")
    baseline_df = pd.merge(df['date'],baseline_df,how='left',on='date')
    baseline_df = baseline_df.fillna(method='ffill').fillna(method='bfill')
    baseline_returns = get_daily_return(baseline_df,value_col_name="close")

    with pyfolio.plotting.plotting_context(font_scale=1.1):
        pyfolio.create_full_tear_sheet(
            returns=test_returns,
            benchmark_rets=baseline_returns,
            set_context=False)