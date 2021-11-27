import os
import time
import numpy as np
import pandas as pd
from rltrade.environments import DayTradingEnv, SmartPortfolioEnv
from stable_baselines3.common.vec_env import DummyVecEnv
from rltrade.data import FeatureEngineer,IBKRDownloader,DayTradeFeatureEngineer
from rltrade.ibkr import api_connect, buy_stock,sell_stock,get_stock_info


from stable_baselines3 import DDPG
from stable_baselines3.common.noise import (
    NormalActionNoise,
    OrnsteinUhlenbeckActionNoise,
)

from rltrade import config

from stable_baselines3 import A2C
from stable_baselines3 import PPO
from stable_baselines3 import TD3
from stable_baselines3.common.noise import (
    NormalActionNoise,
    OrnsteinUhlenbeckActionNoise,
)
from stable_baselines3.common.utils import set_random_seed

from stable_baselines3 import SAC

from rltrade.environments import StockTradingEnv
from rltrade.data import time_series_split


MODELS = {"a2c": A2C, "ddpg": DDPG, "td3": TD3, "sac": SAC, "ppo": PPO}

MODEL_KWARGS = {x: config.__dict__[f"{x.upper()}_PARAMS"] for x in MODELS.keys()}

NOISE = {
    "normal": NormalActionNoise,
    "ornstein_uhlenbeck": OrnsteinUhlenbeckActionNoise,
}

# class TensorboardCallback(BaseCallback):
#     """
#     Custom callback for plotting additional values in tensorboard.
#     """

#     def __init__(self, verbose=0):
#         super(TensorboardCallback, self).__init__(verbose)

#     def _on_step(self) -> bool:
#         try:
#             self.logger.record(key="train/reward", value=self.locals["rewards"][0])
#         except BaseException:
#             self.logger.record(key="train/reward", value=self.locals["reward"][0])
#         return True


class DRLAgent:
    """Provides implementations for DRL algorithms
    Attributes
    ----------
        env: gym environment class
            user-defined class
    Methods
    -------
        train_PPO()
            the implementation for PPO algorithm
        train_A2C()
            the implementation for A2C algorithm
        train_DDPG()
            the implementation for DDPG algorithm
        train_TD3()
            the implementation for TD3 algorithm
        train_SAC()
            the implementation for SAC algorithm
        DRL_prediction()
            make a prediction in a test dataset and get results
    """

    @staticmethod
    def DRL_prediction(model, environment):
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = model.predict(test_obs)
            #account_memory = test_env.env_method(method_name="save_asset_memory")
            #actions_memory = test_env.env_method(method_name="save_action_memory")
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        return account_memory[0], actions_memory[0]

    def __init__(self, env):
        self.env = env
        set_random_seed(42)

    def get_model(
        self,
        model_name,
        policy="MlpPolicy",
        policy_kwargs=None,
        model_kwargs=None,
        verbose=1,
    ):
        if model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if model_kwargs is None:
            model_kwargs = MODEL_KWARGS[model_name]

        if "action_noise" in model_kwargs:
            n_actions = self.env.action_space.shape[-1]
            model_kwargs["action_noise"] = NOISE[model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions)
            )
        print(model_kwargs)
        model = MODELS[model_name](
            policy=policy,
            env=self.env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **model_kwargs,
        )
        return model

    def train_model(self, model, tb_log_name, total_timesteps=5000):
        model = model.learn(total_timesteps=total_timesteps, tb_log_name=tb_log_name)
        return model
    

#################################
# Agent For portfolio Management#
#################################
class SmartDRLAgent:

    def __init__(self,
        model_name,
        ticker_list,
        ticker_col_name,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name,df=None,
        train_period=None,
        test_period=None,
        epochs=5):

        self.df = df
        self.model_name = model_name
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.train_period = train_period
        self.test_period = test_period
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.epochs = epochs
        self.ticker_list = ticker_list
        self.ticker_col_name = ticker_col_name
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = FeatureEngineer(additional_indicators=additional_indicators,
                    stock_indicator_list=tech_indicators,
                    cov_matrix=True) 
        set_random_seed(42)   

    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        if "action_noise" in self.model_kwargs:
            n_actions = environment.action_space.shape[-1]
            self.model_kwargs["action_noise"] = NOISE[self.model_kwargs["action_noise"]](
                mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model

    def make_prediction(self):
        environment = SmartPortfolioEnv(df=self.test,**self.env_kwargs)
        test_env, test_obs = environment.get_sb_env()
        """make a prediction"""
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        return account_memory[0], actions_memory[0]
    
    def get_trade_actions(self,trade_period):
        print("Downloading Data")
        self.trade_period = trade_period
        self.data = IBKRDownloader(start_date=trade_period[0],
                        end_date=trade_period[1],
                        ticker_list=self.ticker_list).fetch_data()
        self.data = self.data.sort_values(by=['date','tic'],ignore_index=True)
        self.price_today = self.data.tail(len(self.ticker_list))['open'].to_numpy()

        print("Creating features. This takes some time")
        temp = self.df.append(self.data).reset_index(drop=True)
        temp = temp.drop_duplicates(subset=['date','tic'])
        temp = self.fe.create_data(temp)
        temp = temp.tail(2*len(self.ticker_list))
        environment = SmartPortfolioEnv(df=temp,**self.env_kwargs)

        print("Loading model")
        model = self.get_model(environment)
        self.model = model.load(self.path+'/model')

        test_env, test_obs = environment.get_sb_env()
        account_memory = []
        actions_memory = []
        test_env.reset()
        for i in range(len(environment.df.index.unique())):
            action, _states = self.model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)
            if i == (len(environment.df.index.unique()) - 2):
              account_memory = test_env.env_method(method_name="save_asset_memory")
              actions_memory = test_env.env_method(method_name="save_action_memory")
            if dones[0]:
                print("hit end!")
                break
        return actions_memory[0].iloc[-1]
    
    def make_trade(self,actions,accountid,demo=True):
        app = api_connect(demo=demo)
        ticker_list = [x.upper() for x in actions.index]
        stock_data = get_stock_info(app,ticker_list,accountid)
        trade_log = pd.DataFrame({"tic":[],"action":[],"quantity":[]})
        for i,tic in enumerate(ticker_list):
            num_stock = (self.env_kwargs['initial_amount'] * actions[i].item())/stock_data[tic][0]
            quantity = int(num_stock-stock_data[tic][1])
            print("in account",stock_data[tic][1])
            if quantity > 0:
                print("buying {} stocks of {}".format(quantity,tic))
                trade_log.loc[len(trade_log.index)] = [tic,"buy",quantity]
                buy_stock(app,tic,quantity)
            elif quantity < 0:
                print("selling {} stocks of {}".format(abs(quantity),tic))
                trade_log.loc[len(trade_log.index)]  = [tic,"sell",abs(quantity)]
                sell_stock(app,tic,abs(quantity))
            else:
                print("Holding ticker {}".format(tic))
                trade_log.loc[len(trade_log.index)]  = [tic,"hold","-"]
        print("Trade Log")
        print(trade_log)
        app.disconnect()
    
    def save_model(self,path:str):
        path = os.path.join(os.getcwd(),path)
        os.makedirs(path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list})
        self.ext_data.to_csv(path+'/ext_data.csv')
        self.df.to_csv(path+'/df.csv')
        self.model.save(path+'/model')

    def load_model(self,path:str):
        path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(path+'/df.csv')
        self.ext_data = pd.read_csv(path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.path = path

    def train_model(self):
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = self.n_steps

        print("Setting up environment...")
        self.env_kwargs['ticker_list'] = self.ticker_list
        environment = SmartPortfolioEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps= self.n_steps * self.epochs ,tb_log_name=self.tb_log_name)
        self.ticker_list = environment.ticker_list
        self.model = model
        self.prev_actions = [0] * len(self.ticker_list)
        self.stock_number = [0] * len(self.ticker_list)
        
    def train_model_filter(self):
        self.train_model()
        print("New ticker list is",self.ticker_list)
        print("Preprocessing Data...")
        self.df = self.df[self.df[self.ticker_col_name].isin(self.ticker_list)]
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        self.model_kwargs['n_steps'] = self.train.index.nunique()
        environment = SmartPortfolioEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=self.n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.model = model

########################
#Agent for day trading #
########################
class SmartDayTradingAgent:

    def __init__(self,
        model_name,
        ticker_list,
        tech_indicators,
        additional_indicators,
        env_kwargs,
        model_kwargs,
        tb_log_name=None,
        df=None,
        train_period=None,
        test_period=None,
        epochs=2
    ):
        self.df = df
        self.model_name = model_name
        self.ticker_list = ticker_list
        self.tech_indicators = tech_indicators
        self.additional_indicators = additional_indicators
        self.env_kwargs = env_kwargs
        self.model_kwargs = model_kwargs
        self.tb_log_name = tb_log_name
        self.train_period = train_period
        self.test_period = test_period
        self.epochs = epochs
        self.train = None
        self.test = None
        self.model = None
        self.ext_data = None

        self.fe = DayTradeFeatureEngineer(additional_indicators= additional_indicators,
                                 stock_indicator_list=tech_indicators)
        set_random_seed(42)
    
    def get_model(
        self,
        environment,
        policy="MlpPolicy",
        policy_kwargs=None,
        verbose=1,
    ):
        train_env, _ = environment.get_sb_env()
        if self.model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if self.model_kwargs is None:
            self.model_kwargs = MODEL_KWARGS[self.model_name]

        model = MODELS[self.model_name](
            policy=policy,
            env=train_env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            **self.model_kwargs,
        )
        return model
    
    def train_model(self):
        print("Preprocessing Data...")
        self.train,self.test = self.fe.train_test_split(self.df,self.train_period,self.test_period)
        n_steps = self.train.index.nunique()
        self.model_kwargs['n_steps'] = n_steps

        print("Setting up environment...")
        environment = DayTradingEnv(df=self.train,**self.env_kwargs)
        model = self.get_model(environment)
        model = model.learn(total_timesteps=n_steps * self.epochs,tb_log_name=self.tb_log_name)
        self.model = model
    
    def save_model(self,path:str):
        path = os.path.join(os.getcwd(),path)
        os.makedirs(path,exist_ok=True)
        self.ext_data = pd.DataFrame({'ticker_list':self.ticker_list})
        self.ext_data.to_csv(path+'/ext_data.csv')
        self.df.to_csv(path+'/df.csv')
        self.model.save(path+'/model')

    def load_model(self,path:str):
        path = os.path.join(os.getcwd(),path)
        self.df = pd.read_csv(path+'/df.csv')
        self.ext_data = pd.read_csv(path+'/ext_data.csv')
        self.ticker_list = self.ext_data['ticker_list'].tolist()
        self.env_kwargs['ticker_list'] = self.ticker_list
        self.path = path


########################
########################
class DRLEnsembleAgent:
    @staticmethod
    def get_model(
        model_name,
        env,
        policy="MlpPolicy",
        policy_kwargs=None,
        model_kwargs=None,
        seed=None,
        verbose=1,
    ):

        if model_name not in MODELS:
            raise NotImplementedError("NotImplementedError")

        if model_kwargs is None:
            temp_model_kwargs = MODEL_KWARGS[model_name]
        else:
            temp_model_kwargs = model_kwargs.copy()

        if "action_noise" in temp_model_kwargs:
            n_actions = env.action_space.shape[-1]
            temp_model_kwargs["action_noise"] = NOISE[
                temp_model_kwargs["action_noise"]
            ](mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
        print(temp_model_kwargs)
        model = MODELS[model_name](
            policy=policy,
            env=env,
            tensorboard_log=None,
            verbose=verbose,
            policy_kwargs=policy_kwargs,
            seed=seed,
            **temp_model_kwargs,
        )
        return model

    @staticmethod
    def train_model(model, model_name, tb_log_name, iter_num, total_timesteps=5000):
        model = model.learn(
            total_timesteps=total_timesteps,
            tb_log_name=tb_log_name,
            # callback=TensorboardCallback(),
        )
        model.save(
            f"{config.TRAINED_MODEL_DIR}/{model_name.upper()}_{total_timesteps//1000}k_{iter_num}"
        )
        return model

    @staticmethod
    def get_validation_sharpe(iteration, model_name):
        """Calculate Sharpe ratio based on validation results"""
        df_total_value = pd.read_csv(
            "results/account_value_validation_{}_{}.csv".format(model_name, iteration)
        )
        sharpe = (
            (4 ** 0.5)
            * df_total_value["daily_return"].mean()
            / df_total_value["daily_return"].std()
        )
        return sharpe

    def __init__(
        self,
        df,
        train_period,
        val_test_period,
        rebalance_window,
        validation_window,
        hmax,
        initial_amount,
        buy_cost_pct,
        sell_cost_pct,
        reward_scaling,
        tech_indicator_list,
        print_verbosity,
        tic_col_name='tic'
    ):

        self.df = df
        self.train_period = train_period
        self.val_test_period = val_test_period

        self.unique_trade_date = df[
            (df.date > val_test_period[0]) & (df.date <= val_test_period[1])
        ].date.unique()
        self.rebalance_window = rebalance_window
        self.validation_window = validation_window

        self.stock_dim = self.df[tic_col_name].nunique()
        self.hmax = hmax
        self.initial_amount = initial_amount
        self.buy_cost_pct = buy_cost_pct
        self.sell_cost_pct = sell_cost_pct
        self.reward_scaling = reward_scaling
        self.tech_indicator_list = tech_indicator_list
        self.print_verbosity = print_verbosity
        set_random_seed(42)

    def DRL_validation(self, model, test_data, test_env, test_obs):
        """validation process"""
        for i in range(len(test_data.index.unique())):
            action, _states = model.predict(test_obs)
            test_obs, rewards, dones, info = test_env.step(action)

    def DRL_prediction(
        self, model, name, last_state, iter_num, turbulence_threshold, initial
    ):
        """make a prediction based on trained model"""

        ## trading env
        trade_data = time_series_split(
            self.df,
            start=self.unique_trade_date[iter_num - self.rebalance_window],
            end=self.unique_trade_date[iter_num],
        )
        trade_env = DummyVecEnv(
            [
                lambda: StockTradingEnv(
                    trade_data,
                    self.hmax,
                    self.initial_amount,
                    self.buy_cost_pct,
                    self.sell_cost_pct,
                    self.reward_scaling,
                    self.tech_indicator_list,
                    turbulence_threshold=turbulence_threshold,
                    initial=initial,
                    previous_state=last_state,
                    model_name=name,
                    mode="trade",
                    iteration=iter_num,
                    print_verbosity=self.print_verbosity,
                )
            ]
        )

        trade_obs = trade_env.reset()

        for i in range(len(trade_data.index.unique())):
            action, _states = model.predict(trade_obs)
            trade_obs, rewards, dones, info = trade_env.step(action)
            if i == (len(trade_data.index.unique()) - 2):
                last_state = trade_env.render()

        df_last_state = pd.DataFrame({"last_state": last_state})
        df_last_state.to_csv(
            "results/last_state_{}_{}.csv".format(name, i), index=False
        )
        return last_state
    
    def get_account_value_df(self):
        unique_trade_date = self.unique_trade_date
        df_trade_date = pd.DataFrame({'datadate':unique_trade_date})

        df_account_value=pd.DataFrame()
        for i in range(self.rebalance_window+self.validation_window, len(unique_trade_date)+1,self.rebalance_window):
            temp = pd.read_csv('results/account_value_trade_{}_{}.csv'.format('ensemble',i))
            df_account_value = df_account_value.append(temp,ignore_index=True)
        # sharpe=(252**0.5)*df_account_value.account_value.pct_change(1).mean()/df_account_value.account_value.pct_change(1).std()
        # print('Sharpe Ratio: ',sharpe)
        df_account_value=df_account_value.join(df_trade_date[self.validation_window:].reset_index(drop=True))
        
        return df_account_value

    def run_ensemble_strategy(
        self, A2C_model_kwargs, PPO_model_kwargs, DDPG_model_kwargs, timesteps_dict
    ):
        """Ensemble Strategy that combines PPO, A2C and DDPG"""
        print("============Start Ensemble Strategy============")
        # for ensemble model, it's necessary to feed the last state
        # of the previous model to the current model as the initial state
        last_state_ensemble = []

        ppo_sharpe_list = []
        ddpg_sharpe_list = []
        a2c_sharpe_list = []

        model_use = []
        validation_start_date_list = []
        validation_end_date_list = []
        iteration_list = []

        insample_turbulence = self.df[
            (self.df.date < self.train_period[1])
            & (self.df.date >= self.train_period[0])
        ]
        insample_turbulence_threshold = np.quantile(
            insample_turbulence["turbulence"].values, 0.90
        )

        start = time.time()
        for i in range(
            self.rebalance_window + self.validation_window,
            len(self.unique_trade_date),
            self.rebalance_window,
        ):
            validation_start_date = self.unique_trade_date[
                i - self.rebalance_window - self.validation_window
            ]
            validation_end_date = self.unique_trade_date[i - self.rebalance_window]

            validation_start_date_list.append(validation_start_date)
            validation_end_date_list.append(validation_end_date)
            iteration_list.append(i)

            print("============================================")
            ## initial state is empty
            if i - self.rebalance_window - self.validation_window == 0:
                # inital state
                initial = True
            else:
                # previous state
                initial = False

            # Tuning trubulence index based on historical data
            # Turbulence lookback window is one quarter (63 days)
            end_date_index = self.df.index[
                self.df["date"]
                == self.unique_trade_date[
                    i - self.rebalance_window - self.validation_window
                ]
            ].to_list()[-1]
            start_date_index = end_date_index - 63 + 1

            historical_turbulence = self.df.iloc[
                start_date_index : (end_date_index + 1), :
            ]

            historical_turbulence = historical_turbulence.drop_duplicates(
                subset=["date"]
            )

            historical_turbulence_mean = np.mean(
                historical_turbulence.turbulence.values
            )

            # print(historical_turbulence_mean)

            if historical_turbulence_mean > insample_turbulence_threshold:
                # if the mean of the historical data is greater than the 90% quantile of insample turbulence data
                # then we assume that the current market is volatile,
                # therefore we set the 90% quantile of insample turbulence data as the turbulence threshold
                # meaning the current turbulence can't exceed the 90% quantile of insample turbulence data
                turbulence_threshold = insample_turbulence_threshold
            else:
                # if the mean of the historical data is less than the 90% quantile of insample turbulence data
                # then we tune up the turbulence_threshold, meaning we lower the risk
                turbulence_threshold = np.quantile(
                    insample_turbulence.turbulence.values, 1
                )

            turbulence_threshold = np.quantile(
                insample_turbulence.turbulence.values, 0.99
            )
            print("turbulence_threshold: ", turbulence_threshold)

            ############## Environment Setup starts ##############
            ## training env
            train = time_series_split(
                self.df,
                start=self.train_period[0],
                end=self.unique_trade_date[
                    i - self.rebalance_window - self.validation_window
                ],
            )
            self.train_env = DummyVecEnv(
                [
                    lambda: StockTradingEnv(
                        train,
                        self.hmax,
                        self.initial_amount,
                        self.buy_cost_pct,
                        self.sell_cost_pct,
                        self.reward_scaling,
                        self.tech_indicator_list,
                        print_verbosity=self.print_verbosity,
                    )
                ]
            )

            validation = time_series_split(
                self.df,
                start=self.unique_trade_date[
                    i - self.rebalance_window - self.validation_window
                ],
                end=self.unique_trade_date[i - self.rebalance_window],
            )
            ############## Environment Setup ends ##############

            ############## Training and Validation starts ##############
            print(
                "======Model training from: ",
                self.train_period[0],
                "to ",
                self.unique_trade_date[
                    i - self.rebalance_window - self.validation_window
                ],
            )
            # print("training: ",len(data_split(df, start=20090000, end=test.datadate.unique()[i-rebalance_window]) ))
            # print("==============Model Training===========")
            print("======A2C Training========")
            model_a2c = self.get_model(
                "a2c", self.train_env, policy="MlpPolicy", model_kwargs=A2C_model_kwargs
            )
            model_a2c = self.train_model(
                model_a2c,
                "a2c",
                tb_log_name="a2c_{}".format(i),
                iter_num=i,
                total_timesteps=timesteps_dict["a2c"],
            )  # 100_000

            print(
                "======A2C Validation from: ",
                validation_start_date,
                "to ",
                validation_end_date,
            )
            val_env_a2c = DummyVecEnv(
                [
                    lambda: StockTradingEnv(
                        validation,
                        self.hmax,
                        self.initial_amount,
                        self.buy_cost_pct,
                        self.sell_cost_pct,
                        self.reward_scaling,
                        self.tech_indicator_list,
                        turbulence_threshold=turbulence_threshold,
                        iteration=i,
                        model_name="A2C",
                        mode="validation",
                        print_verbosity=self.print_verbosity,
                    )
                ]
            )
            val_obs_a2c = val_env_a2c.reset()
            self.DRL_validation(
                model=model_a2c,
                test_data=validation,
                test_env=val_env_a2c,
                test_obs=val_obs_a2c,
            )
            sharpe_a2c = self.get_validation_sharpe(i, model_name="A2C")
            print("A2C Sharpe Ratio: ", sharpe_a2c)

            print("======PPO Training========")
            model_ppo = self.get_model(
                "ppo", self.train_env, policy="MlpPolicy", model_kwargs=PPO_model_kwargs
            )
            model_ppo = self.train_model(
                model_ppo,
                "ppo",
                tb_log_name="ppo_{}".format(i),
                iter_num=i,
                total_timesteps=timesteps_dict["ppo"],
            )  # 100_000
            print(
                "======PPO Validation from: ",
                validation_start_date,
                "to ",
                validation_end_date,
            )
            val_env_ppo = DummyVecEnv(
                [
                    lambda: StockTradingEnv(
                        validation,
                        self.hmax,
                        self.initial_amount,
                        self.buy_cost_pct,
                        self.sell_cost_pct,
                        self.reward_scaling,
                        self.tech_indicator_list,
                        turbulence_threshold=turbulence_threshold,
                        iteration=i,
                        model_name="PPO",
                        mode="validation",
                        print_verbosity=self.print_verbosity,
                    )
                ]
            )
            val_obs_ppo = val_env_ppo.reset()
            self.DRL_validation(
                model=model_ppo,
                test_data=validation,
                test_env=val_env_ppo,
                test_obs=val_obs_ppo,
            )
            sharpe_ppo = self.get_validation_sharpe(i, model_name="PPO")
            print("PPO Sharpe Ratio: ", sharpe_ppo)

            print("======DDPG Training========")
            model_ddpg = self.get_model(
                "ddpg",
                self.train_env,
                policy="MlpPolicy",
                model_kwargs=DDPG_model_kwargs,
            )
            model_ddpg = self.train_model(
                model_ddpg,
                "ddpg",
                tb_log_name="ddpg_{}".format(i),
                iter_num=i,
                total_timesteps=timesteps_dict["ddpg"],
            )  # 50_000
            print(
                "======DDPG Validation from: ",
                validation_start_date,
                "to ",
                validation_end_date,
            )
            val_env_ddpg = DummyVecEnv(
                [
                    lambda: StockTradingEnv(
                        validation,
                        self.hmax,
                        self.initial_amount,
                        self.buy_cost_pct,
                        self.sell_cost_pct,
                        self.reward_scaling,
                        self.tech_indicator_list,
                        turbulence_threshold=turbulence_threshold,
                        iteration=i,
                        model_name="DDPG",
                        mode="validation",
                        print_verbosity=self.print_verbosity,
                    )
                ]
            )
            val_obs_ddpg = val_env_ddpg.reset()
            self.DRL_validation(
                model=model_ddpg,
                test_data=validation,
                test_env=val_env_ddpg,
                test_obs=val_obs_ddpg,
            )
            sharpe_ddpg = self.get_validation_sharpe(i, model_name="DDPG")

            ppo_sharpe_list.append(sharpe_ppo)
            a2c_sharpe_list.append(sharpe_a2c)
            ddpg_sharpe_list.append(sharpe_ddpg)

            print(
                "======Best Model Retraining from: ",
                self.train_period[0],
                "to ",
                self.unique_trade_date[i - self.rebalance_window],
            )
            # Environment setup for model retraining up to first trade date
            # train_full = data_split(self.df, start=self.train_period[0], end=self.unique_trade_date[i - self.rebalance_window])
            # self.train_full_env = DummyVecEnv([lambda: StockTradingEnv(train_full,
            #                                                    self.hmax,
            #                                                    self.initial_amount,
            #                                                    self.buy_cost_pct,
            #                                                    self.sell_cost_pct,
            #                                                    self.reward_scaling,
            #                                                    self.tech_indicator_list,
            #                                                    print_verbosity=self.print_verbosity)])
            # Model Selection based on sharpe ratio
            if (sharpe_ppo >= sharpe_a2c) & (sharpe_ppo >= sharpe_ddpg):
                model_use.append("PPO")
                model_ensemble = model_ppo

                # model_ensemble = self.get_model("ppo",self.train_full_env,policy="MlpPolicy",model_kwargs=PPO_model_kwargs)
                # model_ensemble = self.train_model(model_ensemble, "ensemble", tb_log_name="ensemble_{}".format(i), iter_num = i, total_timesteps=timesteps_dict['ppo']) #100_000
            elif (sharpe_a2c > sharpe_ppo) & (sharpe_a2c > sharpe_ddpg):
                model_use.append("A2C")
                model_ensemble = model_a2c

                # model_ensemble = self.get_model("a2c",self.train_full_env,policy="MlpPolicy",model_kwargs=A2C_model_kwargs)
                # model_ensemble = self.train_model(model_ensemble, "ensemble", tb_log_name="ensemble_{}".format(i), iter_num = i, total_timesteps=timesteps_dict['a2c']) #100_000
            else:
                model_use.append("DDPG")
                model_ensemble = model_ddpg

                # model_ensemble = self.get_model("ddpg",self.train_full_env,policy="MlpPolicy",model_kwargs=DDPG_model_kwargs)
                # model_ensemble = self.train_model(model_ensemble, "ensemble", tb_log_name="ensemble_{}".format(i), iter_num = i, total_timesteps=timesteps_dict['ddpg']) #50_000

            ############## Training and Validation ends ##############

            ############## Trading starts ##############
            print(
                "======Trading from: ",
                self.unique_trade_date[i - self.rebalance_window],
                "to ",
                self.unique_trade_date[i],
            )
            # print("Used Model: ", model_ensemble)
            last_state_ensemble = self.DRL_prediction(
                model=model_ensemble,
                name="ensemble",
                last_state=last_state_ensemble,
                iter_num=i,
                turbulence_threshold=turbulence_threshold,
                initial=initial,
            )
            ############## Trading ends ##############

        end = time.time()
        print("Ensemble Strategy took: ", (end - start) / 60, " minutes")

        df_summary = pd.DataFrame(
            [
                iteration_list,
                validation_start_date_list,
                validation_end_date_list,
                model_use,
                a2c_sharpe_list,
                ppo_sharpe_list,
                ddpg_sharpe_list,
            ]
        ).T
        df_summary.columns = [
            "Iter",
            "Val Start",
            "Val End",
            "Model Used",
            "A2C Sharpe",
            "PPO Sharpe",
            "DDPG Sharpe",
        ]

        return df_summary