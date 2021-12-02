from rltrade import config
from rltrade.data import IBKRDownloader
from rltrade.models import SmartDayTradingAgent

train_period = ('2021-11-23','2021-11-24') #for training the model
test_period = ('2021-11-24','2021-11-26') 

path = 'models/daytrade/dow30'
ticker_list = config.DOW_30_TICKER[:5]
tech_indicators = config.STOCK_INDICATORS_LIST # indicators from stockstats
additional_indicators = config.ADDITIONAL_DAYTRADE_INDICATORS

env_kwargs = {"tech_indicator_list":additional_indicators+tech_indicators}

PPO_PARAMS = {'ent_coef':0.005,
            'learning_rate':0.00001,
            'batch_size':151}

print('Downloading Data')
df = IBKRDownloader(start_date = train_period[0], # first date
                    end_date = test_period[1], #last date
                    ticker_list = ticker_list).fetch_min_data(demo=True) #requires subscription

agent = SmartDayTradingAgent("ppo",
                    df=df,
                    ticker_list=ticker_list,
                    tech_indicators=tech_indicators,
                    additional_indicators=additional_indicators,
                    train_period=train_period,
                    test_period=test_period,
                    env_kwargs=env_kwargs,
                    model_kwargs=PPO_PARAMS,
                    tb_log_name='ppo',
                    epochs=20)

agent.train_model()
agent.save_model(path)