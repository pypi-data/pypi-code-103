from rltrade import config
from rltrade.models import SmartDRLAgent
from rltrade.data import IBKRDownloader
from rltrade.backtests import backtest_plot,backtest_stats

train_period = ('2021-11-23','2021-11-24') #for training the model
test_period = ('2021-11-24','2021-11-26') 
path = 'models/daytrades/etfs'
ticker_list = ['thd','eden','epol','flau','eirl','ewu','ech','fltw','flca','qat','efnl']
tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

env_kwargs = {
    "initial_amount": 100000, 
    "ticker_col_name":"tic",
    "filter_threshold":1, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset','cagr','sortino'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.0001,
            'batch_size':151}

print('Downloading Data')
df = IBKRDownloader(start_date = train_period[0], # first date
                    end_date = test_period[1], #last date
                    ticker_list = ticker_list).fetch_min_data() #requires subscription

agent = SmartDRLAgent("ppo",
                    df=df,
                    ticker_list=ticker_list,
                    ticker_col_name="tic",
                    tech_indicators=tech_indicators,
                    additional_indicators=additional_indicators,
                    train_period=train_period,
                    test_period=test_period,
                    env_kwargs=env_kwargs,
                    model_kwargs=PPO_PARAMS,
                    tb_log_name='ppo',
                    epochs=5)

# agent.train_model()
agent.train_model_filter() #training model on trading period
agent.save_model(path) #save the model for trading

df_daily_return,df_actions = agent.make_prediction() #testing model on testing period

perf_stats_all = backtest_stats(df=df_daily_return,
                                baseline_ticker=agent.ticker_list,
                                value_col_name="daily_return",
                                baseline_start = test_period[0], 
                                baseline_end = test_period[1],
                                mode='min')
print(perf_stats_all)