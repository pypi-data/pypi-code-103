import math
import gym
import numpy as np
import pandas as pd
from gym import spaces
from gym.utils import seeding
import matplotlib.pyplot as plt
from scipy.stats import skew,kurtosis
from stable_baselines3.common.vec_env import DummyVecEnv


class StockTradingEnv(gym.Env):
    """A stock trading environment for OpenAI gym"""
    metadata = {'render.modes': ['human']}

    def __init__(self, 
                df, 
                hmax,                
                initial_amount,
                buy_cost_pct,
                sell_cost_pct,
                reward_scaling,
                tech_indicator_list = [],
                tic_col_name="tic",
                target_metrics=['cagr','sortino','calamar'],
                turbulence_threshold=None,
                make_plots = False, 
                print_verbosity = 10,
                day = 0, 
                initial=True,
                previous_state=[],
                model_name = '',
                mode='',
                iteration=''):
        self.day = day
        self.df = df
        self.stock_dim = self.df[tic_col_name].nunique()
        self.target_metrics = target_metrics
        self.all_metrics = ["asset", "cagr", "sortino", "calamar", "skew", "kurtosis" ]
        # assert self.target_metrics in self.all_metrics,f"wrong metrics available options are:{self.all_metrics}"

        self.hmax = hmax
        self.initial_amount = initial_amount
        self.buy_cost_pct = buy_cost_pct
        self.sell_cost_pct = sell_cost_pct
        self.reward_scaling = reward_scaling
        self.action_space = self.stock_dim
        self.tech_indicator_list = tech_indicator_list
        self.state_space =  1 + 2 * self.stock_dim + len(self.tech_indicator_list)*self.stock_dim
        self.action_space = spaces.Box(low = -1, high = 1,shape = (self.action_space,)) 
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape = (self.state_space,))

        self.data = self.df.loc[self.day,:]
        self.terminal = False     
        self.make_plots = make_plots
        self.print_verbosity = print_verbosity
        self.turbulence_threshold = turbulence_threshold
        self.initial = initial
        self.previous_state = previous_state
        self.model_name=model_name
        self.mode=mode 
        self.iteration=iteration
        # initalize state
        self.state = self._initiate_state()
        
        # initialize reward
        self.reward = 0
        self.turbulence = 0
        self.cost = 0
        self.trades = 0
        self.episode = 0
        # memorize all the total balance change
        self.asset_memory = [self.initial_amount]
        self.rewards_memory = []
        self.actions_memory=[]
        self.date_memory=[self._get_date()]
        #self.reset()
        self._seed()
        


    def _sell_stock(self, index, action):
        def _do_sell_normal():
            if self.state[index+1]>0: 
                # Sell only if the price is > 0 (no missing data in this particular date)
                # perform sell action based on the sign of the action
                if self.state[index+self.stock_dim+1] > 0:
                    # Sell only if current asset is > 0
                    sell_num_shares = min(abs(action),self.state[index+self.stock_dim+1])
                    sell_amount = self.state[index+1] * sell_num_shares * (1- self.sell_cost_pct)
                    #update balance
                    self.state[0] += sell_amount

                    self.state[index+self.stock_dim+1] -= sell_num_shares
                    self.cost +=self.state[index+1] * sell_num_shares * self.sell_cost_pct
                    self.trades+=1
                else:
                    sell_num_shares = 0
            else:
                sell_num_shares = 0

            return sell_num_shares
            
        # perform sell action based on the sign of the action
        if self.turbulence_threshold is not None:
            if self.turbulence>=self.turbulence_threshold:
                if self.state[index+1]>0: 
                    # Sell only if the price is > 0 (no missing data in this particular date)
                    # if turbulence goes over threshold, just clear out all positions 
                    if self.state[index+self.stock_dim+1] > 0:
                        # Sell only if current asset is > 0
                        sell_num_shares = self.state[index+self.stock_dim+1]
                        sell_amount = self.state[index+1]*sell_num_shares* (1- self.sell_cost_pct)
                        #update balance
                        self.state[0] += sell_amount
                        self.state[index+self.stock_dim+1] =0
                        self.cost += self.state[index+1]*self.state[index+self.stock_dim+1]* \
                                    self.sell_cost_pct
                        self.trades+=1
                    else:
                        sell_num_shares = 0
                else:
                    sell_num_shares = 0
            else:
                sell_num_shares = _do_sell_normal()
        else:
            sell_num_shares = _do_sell_normal()

        return sell_num_shares

    
    def _buy_stock(self, index, action):

        def _do_buy():
            if self.state[index+1]>0: 
                #Buy only if the price is > 0 (no missing data in this particular date)       
                available_amount = self.state[0] // self.state[index+1]
                # print('available_amount:{}'.format(available_amount))
                
                #update balance
                buy_num_shares = min(available_amount, action)
                buy_amount = self.state[index+1] * buy_num_shares * (1+ self.buy_cost_pct)
                self.state[0] -= buy_amount

                self.state[index+self.stock_dim+1] += buy_num_shares
                
                self.cost+=self.state[index+1] * buy_num_shares * self.buy_cost_pct
                self.trades+=1
            else:
                buy_num_shares = 0

            return buy_num_shares

        # perform buy action based on the sign of the action
        if self.turbulence_threshold is None:
            buy_num_shares = _do_buy()
        else:
            if self.turbulence< self.turbulence_threshold:
                buy_num_shares = _do_buy()
            else:
                buy_num_shares = 0
                pass

        return buy_num_shares

    def _make_plot(self):
        plt.plot(self.asset_memory,'r')
        plt.savefig('results/account_value_trade_{}.png'.format(self.episode))
        plt.close()

    def step(self, actions):
        self.terminal = self.day >= len(self.df.index.unique())-1
        if self.terminal:
            # print(f"Episode: {self.episode}")
            # if self.make_plots:
            #     self._make_plot()            
            end_total_asset = self.state[0]+ \
                sum(np.array(self.state[1:(self.stock_dim+1)])*np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))
            df_total_value = pd.DataFrame(self.asset_memory)
            tot_reward = self.state[0]+sum(np.array(self.state[1:(self.stock_dim+1)])*np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))- self.initial_amount 
            df_total_value.columns = ['account_value']
            df_total_value['date'] = self.date_memory
            df_total_value['daily_return']=df_total_value['account_value'].pct_change(1)
            sharpe = (252**0.5)*df_total_value['daily_return'].mean()/ \
                   ( df_total_value['daily_return'].std() + 1e-8)
            df_rewards = pd.DataFrame(self.rewards_memory)
            df_rewards.columns = ['account_rewards']
            df_rewards['date'] = self.date_memory[:-1]
            if self.episode % self.print_verbosity == 0:
                print(f"day: {self.day}, episode: {self.episode}")
                print(f"begin_total_asset: {self.asset_memory[0]:0.2f}")
                print(f"end_total_asset: {end_total_asset:0.2f}")
                print(f"total_reward: {tot_reward:0.2f}")
                print(f"total_cost: {self.cost:0.2f}")
                print(f"total_trades: {self.trades}")
                if df_total_value['daily_return'].std() != 0:
                    print(f"Sharpe: {sharpe:0.3f}")
                print("=================================")

            if (self.model_name!='') and (self.mode!=''):
                df_actions = self.save_action_memory()
                df_actions.to_csv('results/actions_{}_{}_{}.csv'.format(self.mode,self.model_name, self.iteration))
                df_total_value.to_csv('results/account_value_{}_{}_{}.csv'.format(self.mode,self.model_name, self.iteration),index=False)
                df_rewards.to_csv('results/account_rewards_{}_{}_{}.csv'.format(self.mode,self.model_name, self.iteration),index=False)
                plt.plot(self.asset_memory,'r')
                plt.savefig('results/account_value_{}_{}_{}.png'.format(self.mode,self.model_name, self.iteration),index=False)
                plt.close()

            return self.state, self.reward, self.terminal, {}

        else:

            actions = actions * self.hmax #actions initially is scaled between 0 to 1
            actions = (actions.astype(int)) #convert into integer because we can't by fraction of shares
            if self.turbulence_threshold is not None:
                if self.turbulence>=self.turbulence_threshold:
                    actions=np.array([-self.hmax]*self.stock_dim)
            begin_total_asset = self.state[0]+ \
            sum(np.array(self.state[1:(self.stock_dim+1)])*np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))
            #print("begin_total_asset:{}".format(begin_total_asset))
            
            argsort_actions = np.argsort(actions)
            sell_index = argsort_actions[:np.where(actions < 0)[0].shape[0]]
            buy_index = argsort_actions[::-1][:np.where(actions > 0)[0].shape[0]]

            for index in sell_index:
                # print(f"Num shares before: {self.state[index+self.stock_dim+1]}")
                # print(f'take sell action before : {actions[index]}')
                actions[index] = self._sell_stock(index, actions[index]) * (-1)
                # print(f'take sell action after : {actions[index]}')
                # print(f"Num shares after: {self.state[index+self.stock_dim+1]}")

            for index in buy_index:
                # print('take buy action: {}'.format(actions[index]))
                actions[index] = self._buy_stock(index, actions[index])

            self.actions_memory.append(actions)

            self.day += 1
            self.data = self.df.loc[self.day,:]    
            if self.turbulence_threshold is not None:     
                self.turbulence = self.data['turbulence'].values[0]
            self.state =  self._update_state()
                           
            end_total_asset = self.state[0]+ \
            sum(np.array(self.state[1:(self.stock_dim+1)])*np.array(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]))
            self.asset_memory.append(end_total_asset)
            self.date_memory.append(self._get_date())

            reward_metrics = {}
            self.reward = 0

            #asset metric calculation
            asset_metric = end_total_asset - begin_total_asset 
            reward_metrics['asset'] = asset_metric

            #cagr calculation
            years = self.day/252
            cagr = ((end_total_asset/begin_total_asset) ** (1/years)) - 1
            reward_metrics['cagr'] = cagr

            #daily return
            df_temp = pd.DataFrame(self.asset_memory)
            df_temp.columns = ['account_value']
            df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
            df_temp.fillna(0,inplace=True)

            #sortino calculation
            sortino = np.mean((df_temp['daily_return'] - 0.1)/ \
                (df_temp.query("daily_return <= 0")['daily_return'].std()+1e-8))
            sortino = 0 if math.isnan(sortino) else sortino
            reward_metrics['sortino'] = sortino

            #sharpe calculation
            sharpe = np.mean((df_temp['daily_return'] - 0.1)/ \
                (df_temp['daily_return'].std()+1e-8))
            sharpe = 0 if math.isnan(sharpe) else sharpe
            reward_metrics['sharpe'] = sharpe
            
            #calamar calculation
            avg_return = df_temp['daily_return'].mean()
            max_drawdown = df_temp['daily_return'].diff(1).min()
            calamar = avg_return/ (max_drawdown + 1e-8)
            calamar = 0 if math.isnan(calamar) else calamar
            reward_metrics['calamar'] = calamar
            
            #skew
            skew_score = skew(df_temp['daily_return'])
            reward_metrics['skew'] = skew_score
            
            kurtosis_score = kurtosis(df_temp['daily_return'])
            reward_metrics['kurtosis'] = kurtosis_score

            for metric in self.target_metrics:
                self.reward += reward_metrics[metric]
                
            self.rewards_memory.append(self.reward)
            self.reward *= self.reward_scaling

        return self.state, self.reward, self.terminal, {}

    def reset(self):  
        #initiate state
        self.state = self._initiate_state()
        
        if self.initial:
            self.asset_memory = [self.initial_amount]
        else:
            previous_total_asset = self.previous_state[0]+ \
            sum(np.array(self.state[1:(self.stock_dim+1)])*np.array(self.previous_state[(self.stock_dim+1):(self.stock_dim*2+1)]))
            self.asset_memory = [previous_total_asset]

        self.day = 0
        self.data = self.df.loc[self.day,:]
        self.turbulence = 0
        self.cost = 0
        self.trades = 0
        self.terminal = False 
        # self.iteration=self.iteration
        self.rewards_memory = []
        self.actions_memory=[]
        self.date_memory=[self._get_date()]
        
        self.episode+=1

        return self.state
    
    def render(self, mode='human',close=False):
        return self.state

    def _initiate_state(self):
        if self.initial:
            # For Initial State
            if len(self.df.tic.unique())>1:
                # for multiple stock
                state = [self.initial_amount] + \
                         self.data.close.values.tolist() + \
                         [0]*self.stock_dim  + \
                         sum([self.data[tech].values.tolist() for tech in self.tech_indicator_list ], [])
            else:
                # for single stock
                state = [self.initial_amount] + \
                        [self.data.close] + \
                        [0]*self.stock_dim  + \
                        sum([[self.data[tech]] for tech in self.tech_indicator_list ], [])
        else:
            #Using Previous State
            if len(self.df.tic.unique())>1:
                # for multiple stock
                state = [self.previous_state[0]] + \
                         self.data.close.values.tolist() + \
                         self.previous_state[(self.stock_dim+1):(self.stock_dim*2+1)]  + \
                         sum([self.data[tech].values.tolist() for tech in self.tech_indicator_list ], [])
            else:
                # for single stock
                state = [self.previous_state[0]] + \
                        [self.data.close] + \
                        self.previous_state[(self.stock_dim+1):(self.stock_dim*2+1)]  + \
                        sum([[self.data[tech]] for tech in self.tech_indicator_list ], [])
        return state

    def _update_state(self):
        if len(self.df.tic.unique())>1:
            # for multiple stock
            state =  [self.state[0]] + \
                      self.data.close.values.tolist() + \
                      list(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]) + \
                      sum([self.data[tech].values.tolist() for tech in self.tech_indicator_list ], [])

        else:
            # for single stock
            state =  [self.state[0]] + \
                     [self.data.close] + \
                     list(self.state[(self.stock_dim+1):(self.stock_dim*2+1)]) + \
                     sum([[self.data[tech]] for tech in self.tech_indicator_list ], [])
                          
        return state

    def _get_date(self):
        if len(self.df.tic.unique())>1:
            date = self.data.date.unique()[0]
        else:
            date = self.data.date
        return date

    def save_asset_memory(self):
        date_list = self.date_memory
        asset_list = self.asset_memory
        #print(len(date_list))
        #print(len(asset_list))
        df_account_value = pd.DataFrame({'date':date_list,'account_value':asset_list})
        return df_account_value

    def save_action_memory(self):
        if len(self.df.tic.unique())>1:
            # date and close price length must match actions length
            date_list = self.date_memory[:-1]
            df_date = pd.DataFrame(date_list)
            df_date.columns = ['date']
            
            action_list = self.actions_memory
            df_actions = pd.DataFrame(action_list)
            df_actions.columns = self.data.tic.values
            df_actions.index = df_date.date
            #df_actions = pd.DataFrame({'date':date_list,'actions':action_list})
        else:
            date_list = self.date_memory[:-1]
            action_list = self.actions_memory
            df_actions = pd.DataFrame({'date':date_list,'actions':action_list})
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

class StockPortfolioEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        hmax,
        initial_amount,
        transaction_cost_pct,
        reward_scaling,
        tech_indicator_list = [],
        tic_col_name="tic",
        target_metrics=['cagr','sortino','calamar'],
        turbulence_threshold=None,
        lookback=252,
        day=0,
    ):
        # super(StockEnv, self).__init__()
        # money = 10 , scope = 1
        self.day = day
        self.lookback = lookback
        self.df = df
        self.stock_dim = self.df[tic_col_name].nunique()
        self.target_metrics = target_metrics
        self.hmax = hmax
        self.initial_amount = initial_amount
        self.transaction_cost_pct = transaction_cost_pct
        self.reward_scaling = reward_scaling
        self.tech_indicator_list = tech_indicator_list

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=0, high=1, shape=(self.stock_dim,))
        # Shape = (34, 30)
        # covariance matrix + technical indicators
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.stock_dim + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.append(
            np.array(self.covs),
            [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            axis=0,
        )
        self.terminal = False
        self.turbulence_threshold = turbulence_threshold
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= len(self.df.index.unique()) - 1

        if self.terminal:
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]
            # plt.plot(df.daily_return.cumsum(), "r")
            # plt.savefig("results/cumulative_reward.png")
            # plt.close()

            # plt.plot(self.portfolio_return_memory, "r")
            # plt.savefig("results/rewards.png")
            # plt.close()

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            weights = self.softmax_normalization(actions)
            self.actions_memory.append(weights)
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]
            self.covs = self.data["cov_list"].values[0]
            self.state = np.append(
                np.array(self.covs),
                [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
                axis=0,
            )
            # print(self.state)
            # calcualte portfolio return
            # individual stocks' return * weight
            portfolio_return = sum(
                ((self.data.close.values / last_day_memory.close.values) - 1) * weights
            )
            # update portfolio value
            begin_total_asset = self.portfolio_value
            new_portfolio_value = self.portfolio_value * (1 + portfolio_return)
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            self.portfolio_return_memory.append(portfolio_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            self.reward = self.get_reward(begin_total_asset,end_total_asset)
            
        return self.state, self.reward, self.terminal, {}

    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric * 0.001

        #cagr calculation
        years = self.day/365
        cagr = ((end_total_asset/begin_total_asset) ** (1/years)) - 1
        reward_metrics['cagr'] = cagr

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        sortino = np.mean((df_temp['daily_return'] - 0.1)/ \
            (df_temp.query("daily_return <= 0")['daily_return'].std()+1e-8))
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino * 10

        #sharpe calculation
        sharpe = np.mean((df_temp['daily_return'] - 0.1)/ \
            (df_temp['daily_return'].std()+1e-8))
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe * 100
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 1000
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score

        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
            
        self.reward *= self.reward_scaling
        return self.reward
    
    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.day = 0
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.append(
            np.array(self.covs),
            [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            axis=0,
        )
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        portfolio_return = self.portfolio_return_memory
        df_account_value = pd.DataFrame(
            {"date": date_list, "daily_return": portfolio_return}
        )
        return df_account_value

    def save_action_memory(self):
        # date and close price length must match actions length
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

################################################
# This environment is for portfolio management #
################################################ 
class SmartPortfolioEnv(gym.Env):

    metadata = {"render.modes": ["human"]}

    def __init__(
        self,
        df,
        initial_amount=100000,
        reward_scaling=1,
        tech_indicator_list = [],
        ticker_list = [],
        ticker_col_name="tic",
        filter_threshold = 0.5,
        transaction_cost = 1.5,
        mode='daily',
        target_metrics=['cagr','sortino','calamar'],
    ):
        self.df = df
        self.stock_dim = self.df[ticker_col_name].nunique()
        self.day = self.df.index.min()
        self.mode = mode
        self.ticker_list = ticker_list
        self.target_metrics = target_metrics
        self.initial_amount = initial_amount
        self.reward_scaling = reward_scaling
        self.ticker_col_name = ticker_col_name
        self.filter_threshold = filter_threshold
        self.transaction_cost = transaction_cost
        self.tech_indicator_list = tech_indicator_list

        # action_space normalization and shape is self.stock_dim
        self.action_space = spaces.Box(low=0, high=1, shape=(self.stock_dim,))
        # covariance matrix + technical indicators
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.stock_dim + len(self.tech_indicator_list), self.stock_dim),
        )

        # load data from a pandas dataframe
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.append(
            np.array(self.covs),
            [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            axis=0,
        )
        self.terminal = False
        # initalize state: inital portfolio return + individual stock return + individual weights
        self.portfolio_value = self.initial_amount

        # memorize portfolio value each step
        self.asset_memory = [self.initial_amount]
        # memorize portfolio return each step
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)

        #per stock memory
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        self._seed(42)

    def step(self, actions):
        self.terminal = self.day >= self.df.index.max()

        if self.terminal:            
            df = pd.DataFrame(self.portfolio_return_memory)
            df.columns = ["daily_return"]

            df_metrics = self.get_reward_per_stock()
            top_n = max(2,int(self.filter_threshold * len(self.ticker_list)))
            self.ticker_list = df_metrics.index.tolist()[:top_n]

            print("=================================")
            print("begin_total_asset:{}".format(self.asset_memory[0]))
            print("end_total_asset:{}".format(self.portfolio_value))

            df_daily_return = pd.DataFrame(self.portfolio_return_memory)
            df_daily_return.columns = ["daily_return"]
            if df_daily_return["daily_return"].std() != 0:
                sharpe = (
                    (252 ** 0.5)
                    * df_daily_return["daily_return"].mean()
                    / df_daily_return["daily_return"].std()
                )
                print("Sharpe: ", sharpe)
            print("=================================")

            return self.state, self.reward, self.terminal, {}

        else:
            weights = self.softmax_normalization(actions)
            self.actions_memory.append(weights)
            last_day_memory = self.data

            # load next state
            self.day += 1
            self.data = self.df.loc[self.day, :]
            self.covs = self.data["cov_list"].values[0]
            self.state = np.append(
                np.array(self.covs),
                [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
                axis=0,)

            #calculate return
            close_values = last_day_memory.close.values
            close_values[close_values==0] = 0.1
            return_values = (self.data.close.values / close_values - 1) * weights
            portfolio_return = sum(return_values)

            #update stocks in portfolio
            stocks_to_buy = [(x*self.initial_amount)/y for x,y in zip(weights,self.data['close'])]
            adjust_stock = [abs(x-y) for x,y in zip(stocks_to_buy,self.stocks_in_portfolio)]
            self.stocks_in_portfolio = stocks_to_buy
            total_transaction_cost = sum([self.transaction_cost for x in adjust_stock if x!=0])

            # update portfolio value
            begin_total_asset = self.portfolio_value
            if self.mode == 'daily':
                new_portfolio_value = (self.portfolio_value * (1 + portfolio_return) ) -total_transaction_cost
            else:
                new_portfolio_value = (self.portfolio_value * (1 + portfolio_return) )
            self.portfolio_value = new_portfolio_value
            end_total_asset = new_portfolio_value

            # save into memory
            self.portfolio_return_memory.append(portfolio_return)
            self.date_memory.append(self.data.date.unique()[0])
            self.asset_memory.append(new_portfolio_value)

            #for per stock values
            self.portfolio_return_per_stock_memory.extend(return_values.ravel().tolist())
            self.ticker_memory.extend(self.data[self.ticker_col_name].values.tolist())
            self.date_memory_per_stock.extend(self.data['date'].values.tolist())
            self.low_values_memory.extend(self.data['low'].values.tolist())
            self.close_values_memory.extend(self.data['close'].values.tolist())

            self.reward = self.get_reward(begin_total_asset,end_total_asset)

            # print(self.reward)
            
        return self.state, self.reward, self.terminal, {}
    
    def get_reward_per_stock(self):

        metrics_list = ['sortino_1year','sortino_3year','sortino_5year',
                        'vix_fix_1year','vix_fix_3year','vix_fix_5year',
                        'calamar_1year','calamar_3year','calamar_5year',
                        'sharpe_1year','sharpe_3year','sharpe_5year']

        df_temp = pd.DataFrame({"tic":self.ticker_memory,
                                "date":self.date_memory_per_stock,
                                "account_value":self.portfolio_return_per_stock_memory,
                                "low":self.low_values_memory,
                                "close":self.close_values_memory})

        df_temp = self.add_sortino(df_temp,1)
        df_temp = self.add_sharpe(df_temp,1)
        df_temp = self.add_clamar(df_temp,1)
        df_temp = self.add_vix_fix(df_temp,1)

        df_temp = self.add_sortino(df_temp,3)
        df_temp = self.add_sharpe(df_temp,3)
        df_temp = self.add_clamar(df_temp,3)
        df_temp = self.add_vix_fix(df_temp,3)

        df_temp = self.add_sortino(df_temp,5)
        df_temp = self.add_sharpe(df_temp,5)
        df_temp = self.add_clamar(df_temp,5)
        df_temp = self.add_vix_fix(df_temp,5)

        df_temp = df_temp.groupby("tic")[metrics_list].mean()
        df_temp = df_temp.sort_values(by=metrics_list,ascending=False)
        return df_temp
            
    
    def add_sortino(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_negative_return'] = temp['daily_return'] 
            temp['daily_return'].fillna(0,inplace=True)
            temp.loc[(temp['daily_negative_return']>0),'daily_negative_return'] = 0
            temp[f'sortino_{years}year'] = temp['daily_negative_return'].rolling(days,min_periods=1).mean() / temp['daily_negative_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'sortino_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_sharpe(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'sharpe_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean() / temp['daily_return'].rolling(days,min_periods=1).std()
            indicator_df = indicator_df.append(temp, ignore_index=True )
        df = df.merge(indicator_df[["tic", "date", f'sharpe_{years}year']], on=["tic", "date"], how="left")
        return df
    
    def add_clamar(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp['daily_return'] = temp['account_value'].pct_change(1)
            temp['daily_drawndown'] = temp['daily_return'].diff(1)
            temp['daily_return'].fillna(0,inplace=True)
            temp[f'calamar_{years}year'] = temp['daily_return'].rolling(days,min_periods=1).mean()/temp['daily_drawndown'].rolling(days,min_periods=1).min()
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'calamar_{years}year']], on=["tic", "date"], how="left")
        return df
    

    def add_vix_fix(self,data,years):
        df = data.copy()
        days = years * 252
        unique_ticker = df.tic.unique()
        indicator_df = pd.DataFrame()
        for ticker in unique_ticker:
            temp = df[(df['tic'] == ticker)].copy()
            temp[f'vix_fix_{years}year'] = ((temp['account_value'].rolling(days,min_periods=1).max() \
                                         - temp['low'])/temp['close'].rolling(days,min_periods=1).max()) * 100
            indicator_df = indicator_df.append(temp, ignore_index=True)
        df = df.merge(indicator_df[["tic", "date", f'vix_fix_{years}year']], on=["tic", "date"], how="left")
        return df

    def get_reward(self,begin_total_asset,end_total_asset):
        reward_metrics = {}
        self.reward = 0

        #asset metric calculation
        asset_metric = end_total_asset - begin_total_asset 
        reward_metrics['asset'] = asset_metric * 0.001

        #cagr calculation
        years = self.day/252
        cagr = ((end_total_asset/begin_total_asset) ** (1/years)) - 1
        reward_metrics['cagr'] = cagr

        #daily return
        df_temp = pd.DataFrame(self.asset_memory)
        df_temp.columns = ['account_value']
        df_temp['daily_return'] = df_temp['account_value'].pct_change(1)
        df_temp['daily_return'].fillna(0,inplace=True)
        df_temp.fillna(0,inplace=True)

        #sortino calculation
        temp = df_temp.query("daily_return <= 0")['daily_return']
        sortino = temp.mean()/ (temp.std() + 1e-8)
        sortino = 0 if math.isnan(sortino) else sortino
        reward_metrics['sortino'] = sortino * 10

        #sharpe calculation
        temp = df_temp['daily_return']
        sharpe = temp.mean()/(temp.std()+1e-8)
        sharpe = 0 if math.isnan(sharpe) else sharpe
        reward_metrics['sharpe'] = sharpe * 100
        
        #calamar calculation
        avg_return = df_temp['daily_return'].mean()
        max_drawdown = df_temp['daily_return'].diff(1).min()
        calamar = avg_return/ (max_drawdown + 1e-8)
        calamar = 0 if math.isnan(calamar) else calamar
        reward_metrics['calamar'] = calamar * 1000
        
        #skew
        skew_score = skew(df_temp['daily_return'])
        reward_metrics['skew'] = skew_score
        
        kurtosis_score = kurtosis(df_temp['daily_return'])
        reward_metrics['kurtosis'] = kurtosis_score

        for metric in self.target_metrics:
            self.reward += reward_metrics[metric]
            
        self.reward *= self.reward_scaling
        return self.reward


    def reset(self):
        self.asset_memory = [self.initial_amount]
        self.stocks_in_portfolio = [0] * len(self.ticker_list)
        self.day = self.df.index.min()
        self.data = self.df.loc[self.day, :]
        self.covs = self.data["cov_list"].values[0]
        self.state = np.append(
            np.array(self.covs),
            [self.data[tech].values.tolist() for tech in self.tech_indicator_list],
            axis=0,
        )
        self.portfolio_value = self.initial_amount
        self.terminal = False
        self.portfolio_return_memory = [0]
        self.actions_memory = [[1 / self.stock_dim] * self.stock_dim]
        self.date_memory = [self.data.date.unique()[0]]
        self.portfolio_return_per_stock_memory = list()
        self.ticker_memory = list()
        self.date_memory_per_stock = list()
        self.low_values_memory = list()
        self.close_values_memory = list()
        return self.state

    def render(self, mode="human"):
        return self.state

    def softmax_normalization(self, actions):
        numerator = np.exp(actions)
        denominator = np.sum(np.exp(actions))
        softmax_output = numerator / denominator
        return softmax_output

    def save_asset_memory(self):
        date_list = self.date_memory
        portfolio_return = self.portfolio_return_memory
        df_account_value = pd.DataFrame(
            {"date": date_list, "daily_return": portfolio_return}
        )
        return df_account_value

    def save_action_memory(self):
        # date and close price length must match actions length
        date_list = self.date_memory
        df_date = pd.DataFrame(date_list)
        df_date.columns = ["date"]

        action_list = self.actions_memory
        df_actions = pd.DataFrame(action_list)
        df_actions.columns = self.data.tic.values
        df_actions.index = df_date.date
        return df_actions

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_sb_env(self):
        e = DummyVecEnv([lambda: self])
        obs = e.reset()
        return e, obs

#######################################
# This environment is for day trading #
#######################################
class DayTradingEnv(gym.Env):
    
    metadata = {"render.model":["human"]}

    def __init__(
        self,
        df,
        tech_indicator_list=[],
    ):
        self.df = df
        self.tick = 0
        self.tech_indicator_list = tech_indicator_list
        self.reward_memory = []

        # 0 (down) or 1 (up)
        self.action_space = spaces.Box(low=-1,high=1,shape=(1,))

        #price,price we short or long,short of long stock,tech indicators
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(3+len(self.tech_indicator_list),)
        )
        self.data = self.df.loc[self.tick,:]
        self.current_symbol = self.data['tic']

        self.state = ([self.data['close']]
                    + [0,0] + self.data[self.tech_indicator_list].tolist())
        
        self.terminal = False
        self.action_memory = []
        self._seed(42)

    
    def step(self,action):
        self.terminal = self.tick >= self.df.index.max()

        if self.terminal:
            print("Total reward",sum(self.reward_memory))
            self.reward = 0
        else:
            self.action_memory.append(action)
            last_tick_memory = self.data
            self.tick += 1
            self.data = self.df.loc[self.tick,:]
            self.reward = 0

            symbol = self.data['tic']
            if symbol != self.current_symbol:
                self.current_symbol = symbol
                self.state = self.reset_new_tic()

            # model predicts down
            action = int(action * 5)
            if action < 0: 

                #if we have no prev long or short
                if self.state[2]==0:
                    self.state = ([self.data['close']]
                            + [last_tick_memory['close'],action] + self.data[self.tech_indicator_list].tolist()) 
                    
                    #when price goes down we get positive reward times action
                    self.reward = (self.state[0] - self.state[1]) * action

                #if it is in long we make reverse trade
                if self.state[2]>0:
                    #we sell the stocks at given price and then short it
                    self.reward = (last_tick_memory['close']-self.state[1]) * self.state[2]
                    self.state = ([self.data['close']]
                            + [last_tick_memory['close'],action] + self.data[self.tech_indicator_list].tolist()) 
                    
                    #reward for shorting
                    self.reward += (self.state[0] - self.state[1]) * action

                # if we have prev short
                if self.state[2]< 0:
                    #get reward for current short
                    self.reward = (last_tick_memory['close']-self.state[1]) * self.state[2]
                    self.state = ([self.data['close']]
                            + [last_tick_memory['close'],action] + self.data[self.tech_indicator_list].tolist()) 

                    #get reward for new short
                    self.reward += (self.state[0] - self.state[1]) * action
            
            #if model predicts up
            elif action > 0:

                #we have no prev long/short
                if self.state[2]==0:
                    self.state = ([self.data['close']]
                            + [last_tick_memory['close'],action] + self.data[self.tech_indicator_list].tolist()) 
                
                    #if price goes up we get reward
                    self.reward = (self.state[0] - self.state[1]) * action

                #we have prev short
                if self.state[2]<0:
                    self.reward = (last_tick_memory['close']-self.state[1]) * self.state[2]
                    self.state = ([self.data['close']]
                            + [last_tick_memory['close'],action] + self.data[self.tech_indicator_list].tolist()) 
                     
                    #reward for long
                    self.reward += (self.state[0] - self.state[1]) * action
                
                # we have prev long
                if self.state[2]>0:
                    #get reward for current short
                    self.reward = (last_tick_memory['close']-self.state[1]) * self.state[2]
                    self.state = ([self.data['close']]
                            + [last_tick_memory['close'],action] + self.data[self.tech_indicator_list].tolist()) 
                    
                    #get reward for long
                    self.reward += (self.state[0] - self.state[1]) * action

            #action is 0
            else:
                #change to current price
                self.state[0] = self.data['close']
                #reward for current long/short 
                self.reward = (self.state[0] - self.state[1]) * self.state[2]

        self.reward_memory.append(self.reward)
        return self.state, self.reward, self.terminal, {}
    
    def reset_new_tic(self):
        self.data = self.df.loc[self.tick,:]

        self.state = ([self.data['close']]
                    + [0,0] + self.data[self.tech_indicator_list].tolist())

        return self.state
    
    def reset(self):
        self.tick = 0
        self.reward_memory = []
        self.data = self.df.loc[self.tick,:]

        self.state = ([self.data['close']]
                    + [0,0] + self.data[self.tech_indicator_list].tolist())
        
        self.terminal = False
        self.action_memory = []
        return self.state
    
    def render(self,mode="human"):
        return self.state
    
    def _seed(self,seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
    
    def get_sb_env(self):
        e = DummyVecEnv([lambda:self])
        obs = e.reset()
        return e,obs