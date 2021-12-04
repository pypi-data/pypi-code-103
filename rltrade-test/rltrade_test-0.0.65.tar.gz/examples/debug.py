from rltrade import config
from rltrade.models import SmartDayTradeAgent
from rltrade.data import IBKRDownloader
from rltrade.backtests import backtest_stats

demo = True
symbol_type = 'future'
train_period = ('2021-11-22','2021-11-25') #for training the model
test_period = ('2021-11-25','2021-11-30') 
path = 'models/daytrades/ESCL'
ticker_list = ['ESZ1','CLF2']
sec_types = ['FUT','FUT']
exchanges = ['GLOBEX','NYMEX']
tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_DAYTRADE_INDICATORS

env_kwargs = {
    "initial_amount": 150000,
    "ticker_col_name":"tic",
    "mode":'min',
    "filter_threshold":1, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset','cagr','sortino'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "transaction_cost":1.5, #transaction cost per order
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.0001,
            'batch_size':151}

print('Downloading Data')
df = IBKRDownloader(start_date = train_period[0], # first date
                    end_date = test_period[1], #last date
                    ticker_list = ticker_list,
                    sec_types=sec_types,
                    exchanges=exchanges,
                    demo=demo,
                    symbol_type=symbol_type
                    ).fetch_min_data()