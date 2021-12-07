"""
市场结构的测试代码部分
"""
import pandas as pd
import numpy as np
import os
import datetime
import statsmodels.api as sm
from hbshare.rm_associated.util.data_loader import get_trading_day_list
from hbshare.quant_research.MarketStructure import MarketHist, get_market_turnover, get_style_factor, \
    AlphaSeries, MarketStructure
from tqdm import tqdm


data_path = "D:\\研究基地\\Analysis"


def run_daily_plot(start_date, end_date):
    date_list = get_trading_day_list(start_date, end_date)
    for date in tqdm(date_list):
        MarketHist(date, '000905').daily_plot()


def run_market_structure(start_date, end_date):
    date_list = get_trading_day_list(start_date, end_date)
    all_res = []
    for date in tqdm(date_list):
        res = MarketStructure(date, '000905').get_construct_result()
        all_res.append(res)

    structure_all = pd.concat(all_res)
    structure_all.to_csv(os.path.join(data_path, "market_structure.csv"))


def run_factor_test(start_date, end_date, mode="1"):
    if mode == "1":
        factor_df = get_market_turnover(start_date, end_date)
    elif mode == "2":
        factor_df = pd.read_csv('D:\\市场微观结构图\\market_factor_save\\win_ratio.csv', index_col=0)
        factor_df['trade_date'] = factor_df.index
        factor_df['trade_date'] = factor_df['trade_date'].apply(lambda x: str(x))
        factor_df = factor_df.set_index('trade_date')
    elif mode == "3":
        factor_df = get_style_factor(start_date, end_date)
        # vol_df = factor_df.rolling(5).std().loc[start_date:]
        # vol_df.rename(columns=lambda x: str(x) + "_vol", inplace=True)
        factor_df = factor_df.loc[start_date:][['size', 'btop', 'growth']]
        # factor_df = pd.concat([factor_df, vol_df], axis=1)
    else:
        factor_df = pd.read_csv('D:\\市场微观结构图\\market_factor_save\\ind_cr.csv', index_col=0)
        factor_df['trade_date'] = factor_df.index
        factor_df['trade_date'] = factor_df['trade_date'].apply(lambda x: str(x))
        factor_df = factor_df.set_index('trade_date')

    alpha_series = AlphaSeries(start_date, end_date).calculate()
    idx = factor_df.index.intersection(alpha_series.index)
    factor_df = factor_df.reindex(idx)
    alpha_excess = alpha_series.reindex(idx)
    factor_df['alpha_excess'] = alpha_excess

    corr_df = factor_df.apply(lambda x: x.rolling(250).corr(factor_df['alpha_excess']).dropna(), axis=0)

    return factor_df


def run_analysis(start_date, end_date):
    structure_df = pd.read_csv(os.path.join(data_path, 'market_structure.csv'), index_col=0)
    structure_df['trade_date'] = structure_df.index
    structure_df['trade_date'] = structure_df['trade_date'].map(str)
    structure_df = structure_df.set_index('trade_date')
    turn_over = pd.read_csv(os.path.join(data_path, 'market_turnover.csv'), dtype={"trade_date": str})
    turn_over['market_A'] /= 1e+4
    turn_over.rename(columns={"market_A": "turn_value"}, inplace=True)
    structure_df = pd.merge(
        turn_over.set_index('trade_date')['turn_value'], structure_df, left_index=True, right_index=True)

    alpha_excess = AlphaSeries(start_date, end_date).calculate()
    idx = structure_df.index.intersection(alpha_excess.index)
    structure_df = structure_df.reindex(idx)
    alpha_excess = alpha_excess.reindex(idx)
    structure_df['alpha_excess'] = alpha_excess

    structure_df.corr()

    # 先尝试一下线性回归
    y = np.array(alpha_excess)
    x = sm.add_constant(np.array(structure_df[['skew', 'lose_med', 'size_return', 'ind_cr']]))
    model = sm.OLS(y, x).fit()
    y_predict = model.predict(x)
    y_predict = pd.Series(index=alpha_excess.index, data=y_predict)
    compare_df = pd.merge(
        alpha_excess.to_frame('true'), y_predict.to_frame('predict'), left_index=True, right_index=True)

    return compare_df


if __name__ == '__main__':
    run_daily_plot('20211206', '20211206')
    # df = run_factor_test('20180101', '20211112', mode="4")
    # print(df)
    # run_market_structure('20200101', '20211108')
    # run_analysis('20200101', '20211108')