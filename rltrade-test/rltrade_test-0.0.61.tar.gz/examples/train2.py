from rltrade import config
from rltrade.models import SmartDRLAgent
from rltrade.data import IBKRDownloader
from rltrade.backtests import backtest_plot,backtest_stats

demo = True
symbol_type = 'future'
train_period = ('2021-11-01','2021-11-25') #for training the model
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

agent = SmartDRLAgent("ppo",
                    df=df,
                    ticker_list=ticker_list,
                    sec_types = sec_types,
                    exchanges=exchanges,
                    ticker_col_name="tic",
                    tech_indicators=tech_indicators,
                    additional_indicators=additional_indicators,
                    train_period=train_period,
                    test_period=test_period,
                    env_kwargs=env_kwargs,
                    model_kwargs=PPO_PARAMS,
                    tb_log_name='ppo',
                    demo=demo,
                    symbol_type=symbol_type,
                    mode='min', # daily or min
                    epochs=5)

# agent.train_model()
agent.train_model() #training model on trading period
agent.save_model(path) #save the model for trading

df_daily_return,df_actions = agent.make_prediction() #testing model on testing period

perf_stats_all = backtest_stats(df=df_daily_return,
                                baseline_ticker=agent.ticker_list,
                                sec_types= agent.sec_types,
                                exchanges=agent.exchanges,
                                value_col_name="daily_return",
                                baseline_start = test_period[0], 
                                baseline_end = test_period[1],
                                demo=demo,
                                symbol_type=symbol_type,
                                mode='min')
print(perf_stats_all)