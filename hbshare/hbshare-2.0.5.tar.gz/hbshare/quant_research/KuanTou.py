"""
宽投指增二号的临时分析
"""
import pandas as pd
from datetime import datetime
import hbshare as hbs
import plotly
from plotly.offline import plot as plot_ly
import plotly.graph_objs as go

plotly.offline.init_notebook_mode(connected=True)

# kt local
nav_kt = pd.read_excel("D:\\研究基地\\B-套利类\\宽投\\净值文件\\宽投资产-指增净值序列20211022.xls", header=1)
nav_kt = nav_kt.rename(
    columns={"净值日期": "tradeDate", "指数增强二号（复权累计净值）": "宽投指数增强二号"})[['tradeDate', '宽投指数增强二号']]
nav_kt['tradeDate'] = nav_kt['tradeDate'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
nav_kt = nav_kt.set_index('tradeDate')
nav_kt = nav_kt[nav_kt.index >= '20200101']


def load_nav_from_sql(fund_id, start_date, end_date):
    sql_script = "SELECT a.jjdm fund_id, b.jzrq TRADEDATE, b.fqdwjz as ADJ_NAV from " \
                 "st_hedge.t_st_jjxx a, st_hedge.t_st_rhb b where a.cpfl = '4' and a.jjdm = b.jjdm " \
                 "and a.jjzt not in ('3') " \
                 "and a.jjdm = '{}' and b.jzrq >= {} and b.jzrq <= {} " \
                 "order by b.jzrq".format(fund_id, start_date, end_date)
    res = hbs.db_data_query("highuser", sql_script, page_size=5000)
    data = pd.DataFrame(res['data']).set_index('TRADEDATE')['ADJ_NAV']

    return data


fund_dict = {"明汯价值成长": "SEE194",
             "启林500指增": "SGY379",
             "黑翼500指增": "SEM323",
             "衍复指增三号": "SJH866",
             "量锐62号": "SGR954",
             "因诺聚配500指增": "SGX346",
             "赫富500指增一号": "SEP463",
             "龙旗红旭500指数增强": "SM4569"}

all_df = []
for name, f_id in fund_dict.items():
    tmp = load_nav_from_sql(f_id, '20190501', '20211022').to_frame(name)
    all_df.append(tmp)

nav_df = pd.concat(all_df, axis=1).sort_index().reindex(nav_kt.index).fillna(method='ffill')
nav_df = pd.merge(nav_kt, nav_df, left_index=True, right_index=True)
nav_df = nav_df / nav_df.iloc[0]


def load_benchmark_data(benchmark_id, start_date, end_date):
    sql_script = "SELECT JYRQ as TRADEDATE, ZQMC as INDEXNAME, SPJG as TCLOSE from funddb.ZSJY WHERE ZQDM = '{}' " \
                 "and JYRQ >= {} and JYRQ <= {}".format(benchmark_id, start_date, end_date)
    res = hbs.db_data_query('readonly', sql_script)
    data = pd.DataFrame(res['data']).rename(columns={"TCLOSE": "benchmark"}).set_index('TRADEDATE')[['benchmark']]

    return data


benchmark_df = load_benchmark_data('000905', nav_df.index[0], nav_df.index[-1])
nav_df = pd.merge(nav_df, benchmark_df, left_index=True, right_index=True)
return_df = nav_df.pct_change().fillna(0.)
tmp = return_df.sub(return_df['benchmark'].squeeze(), axis=0)
tmp = tmp[tmp.columns[:-1]]
tmp = (1 + tmp).cumprod()


def plotly_line(df, title_text, sava_path, figsize=(1200, 500)):
    fig_width, fig_height = figsize
    data = []
    for col in df.columns:
        trace = go.Scatter(
            x=df.index.tolist(),
            y=df[col],
            name=col,
            mode="lines"
        )
        data.append(trace)

    date_list = df.index.tolist()
    tick_vals = [i for i in range(0, len(df), 4)]
    tick_text = [date_list[i] for i in range(0, len(df), 4)]

    layout = go.Layout(
        title=dict(text=title_text),
        autosize=False, width=fig_width, height=fig_height,
        yaxis=dict(tickfont=dict(size=12), showgrid=True),
        xaxis=dict(showgrid=True, tickvals=tick_vals, ticktext=tick_text),
        template='plotly_white'
    )
    fig = go.Figure(data=data, layout=layout)

    plot_ly(fig, filename=sava_path)


plotly_line(tmp, "500指增产品对比", "D:\\kevin\\宽投指增对比.html", figsize=(1500, 800))
