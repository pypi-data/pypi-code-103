import os
from rltrade import config
from rltrade.models import DRLEnsembleAgent
from rltrade.backtests import backtest_plot,backtest_stats
from rltrade.data import FeatureEngineer,YahooDownloader

os.makedirs('results',exist_ok=True)

print('Downloading Data')
df = YahooDownloader(start_date = '2009-01-01',
                        end_date = '2021-01-01',
                        ticker_list = config.DOW_30_TICKER).fetch_data()

print("Preprocessing data")
rebalance_window = 63 # rebalance_window is the number of days to retrain the model
validation_window = 63 # validation_window is the number of days to do validation and trading (e.g. if validation_window=63, then both validation and trading period will be 63 days)
train_period = ('2009-01-01','2019-01-01')
test_period = ('2019-01-01','2021-01-01')

fe = FeatureEngineer(stock_indicators=True,
                    cov_matrix=True,
                    turbulence=True, #required to ensemble
                    stock_indicator_list=config.STOCK_INDICATORS_LIST)

df = fe.create_data(df)

env_kwargs = {
    "hmax": 100, 
    "initial_amount": 1000000, 
    "buy_cost_pct": 0.001, 
    "sell_cost_pct": 0.001, 
    "tech_indicator_list": config.STOCK_INDICATORS_LIST,
    "reward_scaling": 1e-4,
    "print_verbosity":5
}

ensemble_agent = DRLEnsembleAgent(df=df,
                 train_period=train_period,
                 val_test_period=test_period,
                 rebalance_window=rebalance_window, 
                 validation_window=validation_window, 
                 **env_kwargs)

def test_trade():
    A2C_PARAMS = {
                'n_steps': 5,
                'ent_coef': 0.01,
                'learning_rate': 0.0005
                }

    PPO_PARAMS = {
                "ent_coef":0.01,
                "n_steps": 2048,
                "learning_rate": 0.00025,
                "batch_size": 64
                    }

    DDPG_PARAMS = {
                    "buffer_size": 100_000,
                    "learning_rate": 0.000005,
                    "batch_size": 64
                }

    timesteps_dict = {'a2c' : 500, 
                    'ppo' : 500, 
                    'ddpg' : 500}

    df_summary = ensemble_agent.run_ensemble_strategy(A2C_model_kwargs= A2C_PARAMS,
                                                    PPO_model_kwargs= PPO_PARAMS,
                                                    DDPG_model_kwargs = DDPG_PARAMS,
                                                    timesteps_dict= timesteps_dict)

    return df_summary


if __name__ == "__main__":
    df_summary = test_trade()

    print(df_summary.head())

    df_account_value = ensemble_agent.get_account_value_df()

    perf_stats_all = backtest_stats(df=df_account_value,
                                    baseline_ticker='^DJI',
                                    value_col_name="daily_return",
                                    baseline_start = '2019-01-01', 
                                    baseline_end = '2021-01-01')

    print(perf_stats_all)

    backtest_plot(account_value=df_account_value,
                baseline_ticker='^DJI',
                value_col_name="daily_return",
                baseline_start = '2019-01-01', 
                baseline_end = '2021-01-01')