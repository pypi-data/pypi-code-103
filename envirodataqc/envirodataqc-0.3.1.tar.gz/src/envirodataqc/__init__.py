'''
EnviroData QC - 
Quality control and assurance of
environmental data.

API
- QC settings defined in QCconfig.py
- Check Values
    Input
    -- pandas dataframe with datetimes and values
    -- variable type matching a variable listed in QC file
    Output
    -- Dataframe with original data plus flags
- Check Gaps
    Input
    -- pandas dataframe with datetimes and values
    -- ??

'''
from envirodataqc.dataqc import dataqc
from envirodataqc.QCconfig import qcsettings
import numpy as np
import pandas as pd

#Check Values function
def check_vals(data,vartype):
    '''
    Evaluate range, step change, and flatlining
    of input data.
    Inputs
     - Pandas Series of data with datetimeindex
     - variable type matching one of the variables in configuration file
    Output - Pandas dataframe of original input plus flag columns 

    '''
    
    #Load QC Settings for this variable type
    qcranges = qcsettings[vartype]
    qc = dataqc(vartype,qcranges['good'],qcranges['suspicious'],qcranges['ignore_vals'])

    #Create output dataframe
    data_flagged = pd.DataFrame({'values':data})

    #Check range
    data_flagged['flags_range'] = qc.check_range(data)

    #Check step change
    data_flagged['flags_rate'] = qc.check_rate(data)

    #Check flatlining
    data_flagged['flags_flat'] = qc.check_flat(data)

    return data_flagged

def check_gaps(dataindex):
    '''
    Check gaps between data
    Output total of gaps > 1hr
    Input:
    - Pandas datetime index
    Output: total gaps in hours
    **Currently returns np float64
    '''
    #Calculate gaps between points in minutes
    timediff = np.diff(dataindex)
    timediff = timediff.astype(float)/(60*(10**9)) #60 x 10^9 to convert from nanosec

    #Find total of gaps over 1hr
    tot = round(timediff[timediff > 60].sum()/60,1)

    return tot

def daily_quality(data):
    '''
    Calculate daily quality values based on data
    quality flags and spacing of values. 
    Daily quality values defined as:
    1 - good: % good data > 90
              sum where data spacing > 1hr is <= 1hr
    2 - moderate: % good data > 80
                  sum where data spacing > 1hr is <= 2hr
    3 - bad: other criteria not met

    Input
    Pandas series of quality values (0,1,2) with datetime index
    Consolidate multiple columns of flags to one column prior to input
    
    Output:
    Pandas series with quality level 0, 1, 2 (good, moderate, bad) and date for an index
    
    '''
    #Calculate percent good for each day
    percent_good = data.resample('1D').agg(lambda x: x[x==0].size/x.size) 

    #Function for calculating gaps
    def gapcalc(day_hours,max_gap=1):
        '''
        Calculate total gaps in datetimes greater than max_gaps
        Use with Pandas resampler:
        Expects a Pandas series consisting of a column
        of hours into a day
        '''
        day_hours = day_hours.to_numpy()

        #Calculate gaps
        gaps = np.diff(np.concatenate([[0],day_hours,[24]]))

        #Sum
        return gaps[gaps > max_gap].sum()

    day_hours = pd.Series(data.index.hour + data.index.minute/60,index=data.index)
    day_gaps = day_hours.resample('1D').agg(gapcalc)
    
    #Combine series into dataframe
    data_quality = pd.DataFrame({
        'percent_good':percent_good,
        'day_gaps':day_gaps
    })

    #Calculate quality - Note that order matters here! Calc mod first, then good
    data_quality['quality'] = 2 #Assume all bad
    good_data = (data_quality.percent_good >= 0.9) & (data_quality.day_gaps <= 1)
    mod_data = (data_quality.percent_good >= 0.8) & (data_quality.day_gaps <= 2)
    data_quality.loc[mod_data,'quality'] = 1
    data_quality.loc[good_data,'quality'] = 0

    data_quality = data_quality['quality']
    
    return data_quality

     

