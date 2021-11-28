from rltrade import config
from rltrade.models import SmartDRLAgent

#include the dates from valid trading date after test period to yesterday's date
#please do not overlap dates with test period used during training model.
trade_period = ('2021-01-02','2021-11-26') #example testing day
accountid = "DU1770002"
path = 'models/etfs'

tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

env_kwargs = {
    # this is total money spend in value used, to determine how many stocks to buy so please be carefull with it.
    #if there are already stocks availabe in the portfolio It might not buy new stock and sell if there are too many.
    "initial_amount": 100000,
    "ticker_col_name":"tic",
    "filter_threshold":0.5, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset','cagr','sortino'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.0001,
            'batch_size':151}

agent = SmartDRLAgent("ppo",
                    df=None,
                    ticker_list=None,
                    train_period=None,
                    test_period=None,
                    ticker_col_name="tic",
                    tech_indicators=tech_indicators,
                    additional_indicators=additional_indicators,
                    env_kwargs=env_kwargs,
                    model_kwargs=PPO_PARAMS,
                    tb_log_name='ppo',
                    epochs=5)

agent.load_model(path) #same path as save
actions = agent.get_trade_actions(trade_period)
print(actions) #weight given to each stock

agent.make_trade(actions,accountid=accountid,demo=True) #for live account demo is False
agent.save_model(path) #save the changes after trade