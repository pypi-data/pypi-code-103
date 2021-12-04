from rltrade import config
from rltrade.models import DRLAgent
from rltrade.environments import StockTradingEnv
from rltrade.backtests import backtest_plot,backtest_stats
from rltrade.data import FeatureEngineer,YahooDownloader

ticker = config.FAANG_TICKER_DICT['apple']

print('Downloading Data')
df = YahooDownloader(start_date = '2009-01-01',
                    end_date = '2021-01-01',
                    ticker_list = ticker).fetch_data()

print("Preprocessing data")
train_period = ('2009-01-01','2019-01-01')
test_period = ('2019-01-01','2021-01-01')
tech_indicators = config.STOCK_INDICATORS_LIST 
additional_indicators = config.ADDITIONAL_STOCK_INDICATORS

fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators)

train,trade = fe.train_test_split(df,train_period,test_period)

env_kwargs = {
    "hmax": 100, 
    "initial_amount": 100000, 
    "buy_cost_pct": 0.001, 
    "sell_cost_pct":0.001,
    "target_metrics":['cagr','sortino','calamar'], #asset, cagr, sortino, calamar, skew and kurtosis are available options.
    "tech_indicator_list":tech_indicators + additional_indicators, 
    "reward_scaling": 1e-4}

e_train_gym = StockTradingEnv(df=train,**env_kwargs)
env_train, _ = e_train_gym.get_sb_env()

e_trade_gym = StockTradingEnv(df=trade,**env_kwargs)
env_trade,obs_trade = e_trade_gym.get_sb_env()

def test_trade():
    agent = DRLAgent(env = env_train)
    PPO_PARAMS = {'n_steps':2048,
                'ent_coef':0.005,
                'learning_rate':0.0001,
                'batch_size':128}

    model_ppo = agent.get_model("ppo",model_kwargs=PPO_PARAMS)
    print("PPO train start")
    trained_ppo = agent.train_model(model=model_ppo,
                                    tb_log_name='ppo',
                                    total_timesteps=500)
    print("Training PPO success")

    df_account_value,df_actions = DRLAgent.DRL_prediction(model=trained_ppo,
                                                            environment=e_trade_gym)
    print("Trading Success")

    return df_account_value,df_actions


if __name__ == "__main__":
    df_account_value,df_actions = test_trade()
    print(df_account_value.head())

    perf_stats_all = backtest_stats(df=df_account_value,
                                    baseline_ticker='AAPL',
                                    value_col_name="account_value",
                                    baseline_start = '2019-01-01', 
                                    baseline_end = '2021-01-01')

    print(perf_stats_all)
    
    backtest_plot(account_value=df_account_value,
                baseline_ticker='AAPL',
                value_col_name="account_value",
                baseline_start = '2019-01-01', 
                baseline_end = '2021-01-01')