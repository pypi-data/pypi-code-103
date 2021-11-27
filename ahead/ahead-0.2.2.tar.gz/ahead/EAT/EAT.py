import os
import numpy as np
import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects import FloatVector, numpy2ri
from datetime import datetime


stats = importr('stats')
ahead = importr('ahead')

class EAT():

    def __init__(self, h=5, level=95, 
                 weights=[1/3, 1/3, 1/3], 
                 type_pi="E", date_formatting="original"):

        assert len(weights) == 3, "must have 'len(weights) == 3'"
        
        self.h = h
        self.level = level
        self.weights = weights
        self.type_pi = type_pi
        self.date_formatting=date_formatting

        self.fcast = None
        self.averages = None
        self.ranges = None        


    def forecast(self, df):            
        
        # obtain dates 'forecast' -----

        # to be put in utils/ as a function (DRY)
        
        input_dates = df['date'].values 
        n_input_dates = len(input_dates)        
        input_dates_ms = [datetime.strptime(str(input_dates[i]), "%Y-%m-%d").timestamp()*1000 for i in range(n_input_dates)]    

        frequency = pd.infer_freq(pd.DatetimeIndex(input_dates))
        output_dates = np.delete(pd.date_range(start=input_dates[-1], 
            periods=self.h+1, freq=frequency).values, 0).tolist()  
        
        df_dates = pd.DataFrame({'date': output_dates})
        output_dates = pd.to_datetime(df_dates['date']).dt.date                                

        # obtain time series forecast -----

        input_series = df.drop(columns=['date']).values
        y = stats.ts(FloatVector([item for sublist in input_series.tolist() for item in sublist]))
        self.fcast = ahead.eatf(y=y, h=self.h, level=self.level, type_pi=self.type_pi,
                                weights=FloatVector(self.weights))        


        # result -----

        # to be put in utils/ as a function (DRY)

        if (self.date_formatting == "original"): 
            fcast_dates = [datetime.strftime(output_dates[i], "%Y-%m-%d") for i in range(self.h)]            
            self.averages = [[fcast_dates[i], self.fcast.rx2['mean'][i]] for i in range(self.h)]
            self.ranges = [[fcast_dates[i], self.fcast.rx2['lower'][i], self.fcast.rx2['upper'][i]] for i in range(self.h)]            
            return self         
        
        if (self.date_formatting == "ms"):  
            fcast_dates_ms = [int(datetime.strptime(str(output_dates[i]), "%Y-%m-%d").timestamp()*1000) for i in range(self.h)]
            self.averages = [[fcast_dates_ms[i], self.fcast.rx2['mean'][i]] for i in range(self.h)]
            self.ranges = [[fcast_dates_ms[i], self.fcast.rx2['lower'][i], self.fcast.rx2['upper'][i]] for i in range(self.h)]        
            return self         
