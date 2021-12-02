"""
主观股多的估值表分析
"""
import os
import datetime
import pandas as pd
import hbshare as hbs
from hbshare.asset_allocation.macro_index.util import create_table, delete_duplicate_records, WriteToDB
from sqlalchemy import create_engine
from hbshare.rm_associated.config import engine_params
from hbshare.rm_associated.util.config import industry_name, industry_cluster_dict
from hbshare.rm_associated.util.plot_util import draw_timeline_bar
import plotly
import plotly.graph_objs as go
# from plotly.offline import plot as plot_ly

plotly.offline.init_notebook_mode(connected=True)


def plot_render(plot_dic, width=1200, height=800, **kwargs):
    kwargs['output_type'] = 'div'
    plot_str = plotly.offline.plot(plot_dic, **kwargs)
    print('%%angular <div style="height: %ipx; width: %spx"> %s </div>' % (height, width, plot_str))


class HoldingExtractor:
    def __init__(self, data_path, table_name, fund_name, is_increment=1):
        self.data_path = data_path
        self.table_name = table_name
        self.fund_name = fund_name
        self.is_increment = is_increment
        self._load_portfolio_weight()

    def _load_portfolio_weight(self):
        filenames = os.listdir(self.data_path)
        filenames = [x for x in filenames if x.split('.')[-1] in ['xls', 'xlsx']]

        portfolio_weight_list = []
        for file_name in filenames:
            if self.fund_name == '亘曦2号':
                date = file_name.split('.')[0].split('_')[-1][:-3].replace('-', '')
            elif self.fund_name == '富乐一号':
                date = file_name.split('.')[0].split('_')[-2]
            else:
                date = file_name.split('.')[0].split('_')[-1]
            data = pd.read_excel(
                os.path.join(self.data_path, file_name), sheet_name=0, header=3).dropna(subset=['科目代码'])
            net_asset = data[data['科目代码'] == '基金资产净值:']['市值'].values[0]
            # A股
            sh = data[data['科目代码'].str.startswith('11020101')]
            sz = data[data['科目代码'].str.startswith('11023101')]
            cyb = data[data['科目代码'].str.startswith('11024101')]
            kcb = data[data['科目代码'].str.startswith('1102C101')]
            equity_a = pd.concat([sh, sz, cyb, kcb], axis=0)
            equity_a['len'] = equity_a['科目代码'].apply(lambda x: len(x))
            equity_a = equity_a[equity_a['len'] > 8]
            equity_a['ticker'] = equity_a['科目代码'].apply(lambda x: x[-6:])
            equity_a['weight'] = equity_a['市值'] / net_asset
            equity_a = equity_a.rename(columns={"科目名称": "sec_name"})[['ticker', 'sec_name', 'weight']]
            # 港股
            hk1 = data[data['科目代码'].str.startswith('11028101')]
            hk2 = data[(data['科目代码'].str.startswith('11028201')) | (data['科目代码'].str.startswith('11028301'))]
            equity_hk = pd.concat([hk1, hk2], axis=0)
            equity_hk['len'] = equity_hk['科目代码'].apply(lambda x: len(x))
            equity_hk = equity_hk[equity_hk['len'] > 8]
            equity_hk['ticker'] = equity_hk['科目代码'].apply(lambda x: x[-6:])
            equity_hk['weight'] = equity_hk['市值'] / net_asset
            equity_hk = equity_hk.rename(columns={"科目名称": "sec_name"})[['ticker', 'sec_name', 'weight']]
            # 债券
            tmp = data[data['科目代码'] == '1103']
            if tmp.empty:
                bond_df = pd.DataFrame()
            else:
                bond_ratio = tmp['市值'].values[0] / net_asset
                bond_df = pd.DataFrame(columns=['ticker', 'sec_name', 'weight'])
                bond_df.loc[0] = ['b00001', '债券投资', bond_ratio]
            # 基金
            tmp = data[data['科目代码'] == '1105']
            if tmp.empty:
                fund_df = pd.DataFrame()
            else:
                fund_ratio = tmp['市值'].values[0] / net_asset
                fund_df = pd.DataFrame(columns=['ticker', 'sec_name', 'weight'])
                fund_df.loc[0] = ['f00001', '基金投资', fund_ratio]

            df = pd.concat([equity_a, equity_hk, bond_df, fund_df], axis=0)
            df['trade_date'] = date
            portfolio_weight_list.append(df)

        portfolio_weight_df = pd.concat(portfolio_weight_list)
        portfolio_weight_df['fund_name'] = self.fund_name

        return portfolio_weight_df

    def writeToDB(self):
        if self.is_increment == 1:
            data = self._load_portfolio_weight()
            trading_day_list = data['trade_date'].unique().tolist()
            sql_script = "delete from {} where trade_date in ({}) and fund_name = '{}'".format(
                self.table_name, ','.join(trading_day_list), self.fund_name)
            # delete first
            delete_duplicate_records(sql_script)
            # add new records
            WriteToDB().write_to_db(data, self.table_name)
        else:
            sql_script = """
                create table {}(
                id int auto_increment primary key,
                trade_date date not null,
                ticker varchar(10),
                sec_name varchar(20),
                weight decimal(5, 4),
                fund_name varchar(40))
            """.format(self.table_name)
            create_table(self.table_name, sql_script)
            data = self._load_portfolio_weight()
            WriteToDB().write_to_db(data, self.table_name)


class HoldingAnalysor:
    def __init__(self, fund_name, start_date, end_date):
        self.fund_name = fund_name
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_portfolio_weight(self):
        sql_script = "SELECT * FROM subjective_fund_holding where fund_name = '{}' and " \
                     "trade_date >= {} and trade_date <= {}".format(self.fund_name, self.start_date, self.end_date)
        engine = create_engine(engine_params)
        holding_df = pd.read_sql(sql_script, engine)
        holding_df['trade_date'] = holding_df['trade_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y%m%d'))

        return holding_df[['trade_date', 'ticker', 'sec_name', 'weight']]

    @staticmethod
    def _load_shift_date(date):
        trade_dt = datetime.datetime.strptime(date, '%Y%m%d')
        pre_date = (trade_dt - datetime.timedelta(days=100)).strftime('%Y%m%d')

        sql_script = "SELECT JYRQ, SFJJ, SFZM, SFYM FROM funddb.JYRL WHERE JYRQ >= {} and JYRQ <= {}".format(
            pre_date, date)
        res = hbs.db_data_query('readonly', sql_script, page_size=5000)
        df = pd.DataFrame(res['data']).rename(
            columns={"JYRQ": 'calendarDate', "SFJJ": 'isOpen',
                     "SFZM": "isWeekEnd", "SFYM": "isMonthEnd"}).sort_values(by='calendarDate')
        df['isOpen'] = df['isOpen'].astype(int).replace({0: 1, 1: 0})
        df['isWeekEnd'] = df['isWeekEnd'].fillna(0).astype(int)
        df['isMonthEnd'] = df['isMonthEnd'].fillna(0).astype(int)

        trading_day_list = df[df['isMonthEnd'] == 1]['calendarDate'].tolist()

        return trading_day_list[-1]

    @staticmethod
    def _load_benchmark_weight(benchmark_id, shift_date, date):
        sql_script = "SELECT * FROM hsjy_gg.SecuMain where SecuCategory = 4 and SecuCode = '{}'".format(benchmark_id)
        res = hbs.db_data_query('readonly', sql_script)
        index_info = pd.DataFrame(res['data'])
        inner_code = index_info.set_index('SECUCODE').loc[benchmark_id, 'INNERCODE']

        sql_script = "SELECT (select a.SecuCode from hsjy_gp.SecuMain a where a.InnerCode = b.InnerCode and " \
                     "rownum = 1) SecuCode, b.EndDate, b.Weight FROM hsjy_gg.LC_IndexComponentsWeight b WHERE " \
                     "b.IndexCode = '{}' and b.EndDate = to_date('{}', 'yyyymmdd')".format(inner_code, shift_date)
        data = pd.DataFrame(hbs.db_data_query('readonly', sql_script)['data'])
        weight_df = data.rename(
            columns={"SECUCODE": "ticker", "ENDDATE": "effDate", "WEIGHT": "weight"})
        weight_df['benchmark_id'] = benchmark_id
        weight_df['trade_date'] = date

        return weight_df[['trade_date', 'ticker', 'benchmark_id']]

    @staticmethod
    def _load_security_sector(portfolio_weight):
        equity_portfolio_weight = portfolio_weight[portfolio_weight['ticker'].str[0].isin(['0', '3', '6'])]
        trading_day_list = sorted(portfolio_weight['trade_date'].unique())
        cols_list = ['ticker'] + [x.lower() for x in industry_name['sw'].values()]
        security_sector_list = []
        for date in trading_day_list:
            ticker_list = equity_portfolio_weight[equity_portfolio_weight['trade_date'] == date]['ticker'].tolist()
            sql_script = "SELECT {} FROM st_ashare.r_st_barra_style_factor where TRADE_DATE = '{}' and " \
                         "ticker in ({})".format(','.join(cols_list), date,
                                                 ','.join("'{0}'".format(x) for x in ticker_list))
            res = hbs.db_data_query('alluser', sql_script, page_size=5000)
            data = pd.DataFrame(res['data']).set_index('ticker')
            reverse_ind = dict([(value.lower(), key) for (key, value) in industry_name['sw'].items()])
            ind_exposure = data[reverse_ind.keys()].rename(columns=reverse_ind)
            ind_exposure = ind_exposure.reset_index().melt(
                id_vars=['ticker'], value_vars=list(reverse_ind.values()), var_name='industryName1', value_name='sign')
            ind_exposure = ind_exposure[ind_exposure['sign'] == '1']
            ind_exposure['trade_date'] = date
            ind_exposure = ind_exposure.set_index('ticker').reindex(ticker_list).dropna().reset_index()
            security_sector_list.append(ind_exposure)

        security_sector_df = pd.concat(security_sector_list)[['trade_date', 'ticker', 'industryName1']]

        return security_sector_df

    @staticmethod
    def _load_security_value(portfolio_weight):
        equity_portfolio_weight = portfolio_weight[portfolio_weight['ticker'].str[0].isin(['0', '3', '6'])]
        trading_day_list = sorted(portfolio_weight['trade_date'].unique())
        value_data_list = []
        for date in trading_day_list:
            ticker_list = equity_portfolio_weight[equity_portfolio_weight['trade_date'] == date]['ticker'].tolist()
            # 主板
            sql_script = "SELECT PE, PB, DividendRatio, SecuCode FROM " \
                         "(SELECT b.PE, b.PB, b.DividendRatio, a.SecuCode, " \
                         "row_number() over(partition by a.InnerCode order by a.InnerCode) rn FROM " \
                         "hsjy_gp.LC_DIndicesForValuation b join hsjy_gp.SecuMain a on a.InnerCode = b.InnerCode and " \
                         "a.SecuMarket in (83, 90) and a.SecuCategory = 1 WHERE " \
                         "b.TradingDay = to_date('{}', 'yyyymmdd') and a.SecuCode in ({})) " \
                         "WHERE rn = 1".format(date, ','.join("'{0}'".format(x) for x in ticker_list))
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            data_main = pd.DataFrame(res['data']).rename(columns={"PE": "PETTM"})
            # 科创板
            sql_script = "SELECT PETTM, PB, DividendRatio, SecuCode FROM " \
                         "(SELECT b.PETTM, b.PB, b.DividendRatio, a.SecuCode, " \
                         "row_number() over(partition by a.InnerCode order by a.InnerCode) rn FROM " \
                         "hsjy_gp.LC_STIBDIndiForValue b join hsjy_gp.SecuMain a on a.InnerCode = b.InnerCode and " \
                         "a.SecuMarket in (83, 90) and a.SecuCategory = 1 WHERE " \
                         "b.TradingDay = to_date('{}', 'yyyymmdd') and a.SecuCode in ({})) " \
                         "WHERE rn = 1".format(date, ','.join("'{0}'".format(x) for x in ticker_list))
            res = hbs.db_data_query('readonly', sql_script, page_size=5000)
            data_stib = pd.DataFrame(res['data'])

            data = pd.concat([data_main, data_stib]).rename(columns={"SECUCODE": "ticker"})
            del data['ROW_ID']
            data = data.dropna(subset=['ticker'])
            data['trade_date'] = date
            value_data_list.append(data)

        security_value_df = pd.concat(value_data_list)

        return security_value_df

    def _load_data(self):
        portfolio_weight_df = self._load_portfolio_weight()
        date_list = sorted(portfolio_weight_df['trade_date'].unique())
        benchmark_weight = []
        for date in date_list:
            shift_date = self._load_shift_date(date)
            weight_300 = self._load_benchmark_weight('000300', shift_date, date)
            weight_500 = self._load_benchmark_weight('000905', shift_date, date)
            weight_1000 = self._load_benchmark_weight('000852', shift_date, date)
            benchmark_weight.append(pd.concat([weight_300, weight_500, weight_1000]))

        benchmark_weight = pd.concat(benchmark_weight)

        security_sector_df = self._load_security_sector(portfolio_weight_df)

        security_value_df = self._load_security_value(portfolio_weight_df)

        self.data_param = {"portfolio_weight": portfolio_weight_df,
                           "benchmark_weight": benchmark_weight,
                           "security_sector_df": security_sector_df,
                           "security_value_df": security_value_df}

    @staticmethod
    def _calculate_asset_allo_series(portfolio_weight):
        date_list = sorted(portfolio_weight['trade_date'].unique())
        equity_a_series = portfolio_weight[portfolio_weight['ticker'].str[0].isin(['0', '3', '6'])].groupby(
            'trade_date')['weight'].sum().reindex(date_list).fillna(0.).to_frame('A股')
        equity_hk_series = portfolio_weight[portfolio_weight['ticker'].str.startswith('H')].groupby(
            'trade_date')['weight'].sum().reindex(date_list).fillna(0.).to_frame('港股')
        bond_series = portfolio_weight[portfolio_weight['ticker'].str.startswith('b')].groupby(
            'trade_date')['weight'].sum().reindex(date_list).fillna(0.).to_frame('债券')
        fund_series = portfolio_weight[portfolio_weight['ticker'].str.startswith('f')].groupby(
            'trade_date')['weight'].sum().reindex(date_list).fillna(0.).to_frame('基金')
        asset_allo_series = pd.concat([equity_a_series, equity_hk_series, bond_series, fund_series], axis=1)
        asset_allo_series['现金类'] = 1 - asset_allo_series.sum(axis=1)

        return asset_allo_series

    @staticmethod
    def _calculate_ind_allo_series(portfolio_weight, security_sector_df):
        weight_df = pd.merge(portfolio_weight, security_sector_df, on=['trade_date', 'ticker'])
        grouped_df = weight_df.groupby(['trade_date', 'industryName1'])['weight'].sum().reset_index()
        pivot_df = pd.pivot_table(
            grouped_df, index='trade_date', columns='industryName1', values='weight').sort_index().fillna(0.)

        sector_df = pd.DataFrame(index=pivot_df.index, columns=industry_cluster_dict.keys())
        for key, value in industry_cluster_dict.items():
            value_include = [x for x in value if x in pivot_df.columns]
            sector_df[key] = pivot_df[value_include].sum(axis=1)

        return pivot_df, sector_df

    @staticmethod
    def plotly_area(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        cols = df.index.tolist()

        data = []
        for col in cols:
            tmp = go.Scatter(
                x=df.columns.tolist(),
                y=df.loc[col].values,
                name=col,
                mode='lines',
                line=dict(width=0.5),
                fill='tonexty',
                stackgroup='one')
            data.append(tmp)

        layout = go.Layout(
            title=title_text,
            autosize=False,
            width=fig_width,
            height=fig_height,
            showlegend=True,
            xaxis=dict(type='category'),
            yaxis=dict(
                type='linear',
                range=[1, 100],
                dtick=20,
                ticksuffix='%'))

        # fig = go.Figure(data=data, layout=layout)
        # plot_ly(fig, filename=save_path, auto_open=False)

        plot_render({"data": data, "layout": layout})

    @staticmethod
    def plotly_line(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize
        data = []
        for col in df.columns:
            trace = go.Scatter(
                x=df.index.tolist(),
                y=df[col],
                name=col,
                mode="lines+markers"
            )
            data.append(trace)

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), tickformat=',.0%', showgrid=True),
            xaxis=dict(showgrid=True),
            template='plotly_white'
        )

        plot_render({"data": data, "layout": layout})

    @staticmethod
    def plotly_double_y_line(df, title_text, figsize=(1200, 600)):
        fig_width, fig_height = figsize

        trace0 = go.Scatter(x=df.index.tolist(), y=df[df.columns[0]], mode="lines+markers", name=df.columns[0])
        trace1 = go.Scatter(x=df.index.tolist(), y=df[df.columns[1]], mode="lines+markers", name=df.columns[1],
                            yaxis='y2')

        data = [trace0, trace1]

        layout = go.Layout(
            title=dict(text=title_text),
            autosize=False, width=fig_width, height=fig_height,
            yaxis=dict(tickfont=dict(size=12), showgrid=False),
            yaxis2=dict(overlaying='y', side='right'),
            xaxis=dict(showgrid=True),
            template='plotly_white'
        )

        plot_render({"data": data, "layout": layout})

    def get_construct_result(self):
        portfolio_weight = self.data_param['portfolio_weight']
        benchmark_weight = self.data_param['benchmark_weight']
        security_sector_df = self.data_param['security_sector_df']
        security_value_df = self.data_param['security_value_df']
        # 资产配置时序
        asset_allo_series = self._calculate_asset_allo_series(portfolio_weight)
        # 行业配置时序
        industry_allo_df, sector_allo_df = self._calculate_ind_allo_series(portfolio_weight, security_sector_df)
        industry_cr = \
            pd.concat([industry_allo_df.apply(lambda x: x.nlargest(1).sum(), axis=1).to_frame('第一大行业'),
                       industry_allo_df.apply(lambda x: x.nlargest(3).sum(), axis=1).to_frame('前三大行业'),
                       industry_allo_df.apply(lambda x: x.nlargest(5).sum(), axis=1).to_frame('前五大行业')], axis=1)
        # 重仓持股
        equity_weight = portfolio_weight[~portfolio_weight['ticker'].str[0].isin(['b', 'f'])]
        equity_weight = pd.pivot_table(
            equity_weight, index='trade_date', columns='sec_name', values='weight').sort_index()
        tmp = equity_weight.fillna(0.)
        equity_cr = pd.concat([tmp.apply(lambda x: x.nlargest(3).sum(), axis=1).to_frame('cr3'),
                               tmp.apply(lambda x: x.nlargest(5).sum(), axis=1).to_frame('cr5'),
                               tmp.apply(lambda x: x.nlargest(10).sum(), axis=1).to_frame('cr10')], axis=1)
        # 平均PE/PB
        security_value_df = pd.merge(security_value_df, portfolio_weight, on=['trade_date', 'ticker']).dropna()
        average_pe = security_value_df.groupby('trade_date').apply(
            lambda x: (x['weight'] * x['PETTM']).sum() / x['weight'].sum()).to_frame('平均市盈率')
        average_pb = security_value_df.groupby('trade_date').apply(
            lambda x: (x['weight'] * x['PB']).sum() / x['weight'].sum()).to_frame('平均市净率')
        average_pe_pb = pd.concat([average_pe, average_pb], axis=1)
        # 持仓宽基分布
        df = portfolio_weight[portfolio_weight['ticker'].str[0].isin(['0', '3', '6'])]
        df = pd.merge(df, benchmark_weight, on=['trade_date', 'ticker'], how='left').fillna('other')
        bm_dis = df.groupby(['trade_date', 'benchmark_id'])['weight'].sum().reset_index()
        bm_dis = pd.pivot_table(
            bm_dis, index='trade_date', columns='benchmark_id', values='weight').sort_index().fillna(0.)
        map_dict = {"000300": "沪深300", "000905": "中证500", "000852": "中证1000", "other": "1800以外"}
        bm_dis.columns = [map_dict[x] for x in bm_dis.columns]
        bm_dis = bm_dis[['沪深300', '中证500', '中证1000', '1800以外']]

        self.plotly_area(100 * asset_allo_series.T, '资产配置时序图')
        self.plotly_area(100 * industry_allo_df.T, '行业配置时序图')
        self.plotly_line(industry_cr, '持股行业集中度时序图')
        tl_bar = draw_timeline_bar(equity_weight)
        # tl_bar.render('D:\\主观股多估值表基地\\图表所在\\持仓明细tl图.html')
        self.plotly_line(equity_cr, "持股集中度时序图")
        self.plotly_double_y_line(average_pe_pb.round(1), "持股估值水平时序图")
        self.plotly_area(100 * bm_dis.T, '宽基成分权重配置时序图')

        return tl_bar


if __name__ == '__main__':
    name = '新方程泰暘臻选1期'
    # name = '新方程望正精英鹏辉'
    # name = '新方程域秀智享5号'
    # name = '亘曦2号'
    # name = '富乐一号'
    # HoldingExtractor(data_path='D:\\主观股多估值表基地\\{}'.format(name), table_name="subjective_fund_holding",
    #                  fund_name=name, is_increment=1).writeToDB()
    HoldingAnalysor(name, start_date='20191201', end_date='20211201').get_construct_result()