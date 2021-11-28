import time
from pytz import timezone
from rltrade import config
from datetime import datetime
from rltrade.models import SmartDRLAgent

trade_period = ('2021-11-25','2021-11-27') #(last test date, yesterdays date)
today_date = '2021-11-28'
accountid = "DU1770002"
path = 'models/daytrades/futures'

tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_DAYTRADE_INDICATORS

env_kwargs = {
    "initial_amount": 100000,
    "ticker_col_name":"tic",
    "filter_threshold":0.5, #between 0.1 to 1, select percentage of top stocks 0.3 means 30% of top stocks
    "target_metrics":['asset','cagr','sortino'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.0001,
            'batch_size':151}

tz = timezone('EST')
start_time = datetime.strptime(today_date+" 09:30:00","%Y-%m-%d %H:%M:%S")
current_time = datetime.strptime(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime(today_date+" 15:59:00","%Y-%m-%d %H:%M:%S")

while current_time < end_time:
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
                        epochs=5,
                        mode='min')

    duration = (current_time-start_time).seconds

    agent.load_model(path) #same path as save
    actions = agent.get_day_trade_actions(current_time,duration,trade_period)
    print(actions) #weight given to each stock

    agent.make_day_trade(actions,accountid=accountid,demo=True) #for live account demo is False
    agent.save_model(path) #save the changes after trade

    current_time = datetime.strptime(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")