import numpy as np
import pandas as pd
from scipy.optimize import minimize

class MPT:
    def __init__(self, env):        
        self.env = env

    def get_daily_returns(self, stocks, start, end, source='yahoo'):
        """
        Fetch daily assets' data from source and compute daily log returns.
        Outputs a Pandas DataFrame in which each column has the daily log
        returns of an asset over the period start to end.
        Params
        ======
            stocks: assets
            start: the start date
            end: the end date
                    
        """
        data = [web.DataReader(s, source, start, end)['Adj Close'] for s in stocks]
        daily_returns = pd.concat(data, axis=1).apply(lambda x: np.log(x/x.shift(1)))
        daily_returns.columns = stocks
        return daily_returns


    def get_stats(self, weights, retvct, covmat):
        """
        Compute portfolio anualized returns, volatility and ret/vol.
        Params
        ======
            weights
            retvct
            covmat: covariance matrix
            
        """
        ret = np.dot(retvct, weights)*252
        std = np.sqrt(np.dot(weights, np.dot(covmat*252, weights)))
        return [ret, std, ret/std]


    def get_stats2(self, rets, weights):
        """
        Same as get_stats, but takes DataFrame with returns as input.
        """
        retvct = rets.mean().to_numpy()
        covmat = rets.cov().to_numpy()   

        return self.get_stats(weights, retvct, covmat)


    def compute_frontier(self, rets, N=30):
        """
        Compute N points on the efficient frontier. 
        An added contraint is that each weight >= 0, i.e., no short selling.
        """
        assert N > 2

        retvct  = rets.mean().to_numpy()
        covmat  =  rets.cov().to_numpy()   

        max_ret = rets.mean().max()*252
        min_ret = get_stats(optimal_volatility(retvct, covmat), retvct, covmat)[0]

        tgt_rets = [min_ret + i*(max_ret-min_ret)/N for i in range(N)]
        weights  = [optimal_returns(retvct, covmat, tgt) for tgt in tgt_rets]
        points   = [get_stats(x, retvct, covmat) for x in weights]

        return weights, points


    def optimal_returns(self, retvct, covmat, tgt):
        """
        Find the optimal weights for the expected return.
        """
        cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'ineq', 'fun': lambda x: x},
                {'type': 'eq', 'fun': lambda x: get_stats(x, retvct, covmat)[0] - tgt})

        func = lambda x: get_stats(x, retvct, covmat)[1]

        x0 = [1./len(retvct) for x in retvct]
        return minimize(func, x0, constraints=cons, method='SLSQP').x
        

    def optimal_volatility(self, retvct, covmat):
        """
        Find the weights for the portfolio with least variance.
        """
        cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'ineq', 'fun': lambda x: x})

        func = lambda x: get_stats(x, retvct, covmat)[1]

        x0 = [1./len(retvct) for x in retvct]
        return minimize(func, x0, constraints=cons, method='SLSQP').x


    def optimal_sharpe_ratio(self, retvct, covmat):
        """
        Find the weights for the portfolio with maximized ret/vol (Sharpe Ratio).
        """
        cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'ineq', 'fun': lambda x: x})

        func = lambda x: -self.get_stats(x, retvct, covmat)[2]

        x0 = [1./len(retvct) for x in retvct]
        return minimize(func, x0, constraints=cons, method='SLSQP').x


    def optimize(self, rets, opt_type, tgt=None):
        """
        Optimize depending on criteria

        Params
        =====
        rets: returns
        opt-type: Type of optimization            
        """        
        retvct  = rets.mean().to_numpy()
        covmat  =  rets.cov().to_numpy()   

        if opt_type == 'ret':
            return optimal_returns(retvct, covmat, tgt)
        elif opt_type == 'vol':
            return optimal_volatility(retvct, covmat)
        elif opt_type == 'sha':
            return optimal_sharpe_ratio(retvct, covmat)
        
    def learn(self, daily_returns):
        """
        Trains the agent

        Params
        ======
            daily_returns: daily returns
        """        
        retvct = daily_returns.mean().to_numpy()
        covmat = daily_returns.cov().to_numpy()
        self.weights = self.optimal_sharpe_ratio(retvct, covmat)
        
    def predict(self, state=None):
        """
        Returns the predicted values
            
        """        
        return np.clip(self.weights, 0, 1)
        

if __name__ == "__main__":
    stocks = ['MSFT', 'AAPL', 'JNJ', 'JPM', 'GOOG']
    mpt = MPT(stocks)
    daily_returns = mpt.get_daily_returns(stocks, '01/01/2014', '31/12/2016')
    
    print(x)

    print(mpt.get_stats2(daily_returns, x))