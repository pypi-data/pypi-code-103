"""
套利和T0类策略收益统计
"""
import numpy as np
from sqlalchemy import create_engine
from hbshare.rm_associated.util.data_loader import get_trading_day_list
import pandas as pd
import numpy as np
import datetime
import hbshare as hbs

sql_params = {
    "ip": "192.168.223.152",
    "user": "readonly",
    "pass": "c24mg2e6",
    "port": "3306",
    "database": "work"
}

engine_params = "mysql+pymysql://{}:{}@{}:{}/{}".format(sql_params['user'], sql_params['pass'], sql_params['ip'],
                                                        sql_params['port'], sql_params['database'])


fund_list = ['SEF694', 'SNP300', 'SJB143', 'SE8723', 'SEK201', 'SGP290',
             'SJS027', 'SW0500',
             'SCP765', 'SLL241', 'SND168', 'SEP929', 'SGL202']

under_research = {
    "弘量君享量化CTA": "SQR403",
    "时代复兴微观一号": "SX1152",
    "弘源量化1号": "SK1274",
    "锐汇量化专享一号": "SGH587",
    "盛冠达时代匠心4号": "SJY896",
    "盛冠达股指套利3号": "SGS597",
    "博普量化对冲6号1期": "SLJ372"
}


def get_fund_data_from_work(start_date, end_date, fund_id):
    sql_script = "SELECT name, t_date, nav FROM fund_data where " \
                 "t_date >= {} and t_date <= {} and code = '{}'".format(start_date, end_date, fund_id)
    engine = create_engine(engine_params)
    data = pd.read_sql(sql_script, engine)
    data['t_date'] = data['t_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))

    return data

def get_fund_data_from_sql(start_date, end_date, fund_dict):
    nav_series_list = []
    for name, fund_id in fund_dict.items():
        sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                     "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                     "and a.jjzt not in ('3') " \
                     "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                     "order by b.jzrq".format(fund_id, start_date, end_date)
        res = hbs.db_data_query("highuser", sql_script, page_size=5000)
        data = pd.DataFrame(res['data']).set_index('TRADEDATE')['ADJ_NAV']
        data.name = name
        nav_series_list.append(data)
    df = pd.concat(nav_series_list, axis=1).sort_index()

    return df


def calculate(nav_series):
    ret_series = nav_series.pct_change().dropna()

    tmp = ret_series[ret_series.index >= '20210101']
    ret1 = (1 + tmp).prod() - 1

    tmp = ret_series[ret_series.index >= '20201119']
    ret2 = (1 + tmp).prod() - 1

    ret3 = np.power((1 + ret_series).prod(), (50. / len(ret_series))) - 1

    return [ret1, ret2, ret3]


if __name__ == '__main__':
    s_date = '20191119'
    e_date = '20211119'

    date_list = get_trading_day_list(s_date, e_date, frequency='week')

    data1 = []
    for f_id in fund_list:
        data1.append(get_fund_data_from_work(s_date, e_date, f_id).set_index('t_date').reindex(date_list))

    data1 = pd.concat(data1)
    data1 = pd.pivot_table(data1.reset_index(), index='t_date', columns='name', values='nav').sort_index()
    data1.index.name = 'TRADEDATE'

    data2 = get_fund_data_from_sql(s_date, e_date, under_research).reindex(date_list)

    nav_df = pd.concat([data1, data2], axis=1)