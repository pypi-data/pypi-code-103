import numpy as np
import pandas as pd

class grid:
    """
    Simple class to construct and hold spatial grid for the model
    """
    
    def __init__(self,options):
        # create grid 
        v0 = np.linspace(options.start0,options.end0,options.n0)
        v1 = np.linspace(options.start1,options.end1,options.n1)
        self.x = {}
        self.x[0], self.x[1] = np.meshgrid(v0,v1)
        # calculate distances between grids
        dp0 = v0[1:]-v0[:-1]
        dp0 = np.append(dp0,dp0[-1])
        dm0 = v0[1:]-v0[:-1]
        dm0 = np.append(dm0[0],dm0)
        dp1 = v1[1:]-v1[:-1]
        dp1 = np.append(dp1,dp1[-1])
        dm1 = v1[1:]-v1[:-1]
        dm1 = np.append(dm1[0],dm1)
        self.dm = {}
        self.dp = {}
        self.dm[0], self.dm[1] = np.meshgrid(dm0,dm1)
        self.dp[0], self.dp[1] = np.meshgrid(dp0,dp1)
