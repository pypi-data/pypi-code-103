import pandas as pd
import numpy as np
from .mpt import MPT

class BaselineAgent():
    """This is the agent class for the Baseline Models
    
    """
    def __init__(self, name, env):
        """Initializes a baseline model

        Args:
            name (str): One of MPT, BuyAndHold, Random, or Uniform
            env: Portfolio Gym Environment
        """        
        self.name = name
        self.env = env
        self.action_space = self.env.action_space.shape[-1]
        self.env.random_start_range = 0
        
    def learn(self, timesteps = None, print_every = None):
        """
        Trains the baseline models
        """        
        if self.name == 'MPT':
            self.model = MPT(self.env)
            daily_returns = self.env.reset()
            daily_returns = daily_returns.reshape(self.env.n, -1)
            daily_returns = pd.DataFrame(daily_returns).T
            self.model.learn(daily_returns)
        elif self.name == 'BuyAndHold':
            daily_returns = self.env.reset()
            daily_returns = daily_returns.reshape(self.env.n, -1)
            daily_returns = daily_returns.mean(axis = 1)
            clipped_returns = np.clip(daily_returns, 0, np.inf)
            self.model = clipped_returns/sum(clipped_returns)
        else:
            self.env.reset()
    
    def predict(self, obs):
        """Returns agent's action

        Args:
            obs (array_like): Current state

        Returns:
            action: Agent's action
        """        
        if self.name == 'Uniform':
            weights = [1/self.env.n] * self.env.n
        elif self.name == 'Random':
            weights = np.random.random(size = self.env.n)
            weights = weights/weights.sum()
        elif self.name == 'BuyAndHold':
            weights =  self.model
        elif self.name == 'MPT':
            weights = self.model.predict(obs)
        else:
            assert False, 'Model name must be one of Uniform, Random, BuyAndHold, or MPT'        
        
        if self.action_space > self.env.n:
                weights = np.append(weights, 0)
        return weights
            
            
            