import pandas as pd
from rltrade import config
from rltrade.models import SmartDRLAgent
from rltrade.data import IBKRDownloader
from rltrade.backtests import backtest_stats, get_daily_return

demo = True
symbol_type = 'stock'
train_period = ('2015-01-01','2020-01-01') #for training the model
test_period = ('2021-01-01','2021-11-29') #for trading and backtesting
path = 'models/etfs'

ticker_list = ['thd','eden','epol','flau','eirl','ewu','ech','fltw','flca','qat','efnl']
sec_types = ['STK','STK','STK','STK','STK','STK','STK','STK','STK','STK','STK']
exchanges = ['SMART','SMART','SMART','SMART','SMART','SMART','SMART','SMART','SMART','SMART','SMART']
tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

env_kwargs = {
    "initial_amount": 100000, 
    "ticker_col_name":"tic",
    "mode":'daily',
    "filter_threshold":0.5, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset','cagr','sortino'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}
    
PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.0001,
            'batch_size':151}

# print('Downloading Data')
# df = IBKRDownloader(start_date = train_period[0], # first date
#                     end_date = test_period[1], #last date
#                     ticker_list = ticker_list,
#                     sec_types=sec_types,
#                     exchanges=exchanges,
#                     symbol_type=symbol_type).fetch_data() #requires subscription

# df.to_csv("testdata/df.csv",index=False)

df = pd.read_csv('testdata/df.csv')

print(df.head())

df = get_daily_return(df,value_col_name="close")

print(df)

