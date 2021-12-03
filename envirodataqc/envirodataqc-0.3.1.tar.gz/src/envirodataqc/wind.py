'''
Special QC Algorithms for wind
'''
import numpy as np
import pandas as pd

def check_windsp_ratio(data):
    '''
    Evaluate wind speeds for internal consistency
    - Calculate ratio of max/ave values (typically for 24hr period)
    Input
     - Dataframe of wind speed values

    Algorithm:
    Calculate average (numerical integral) of values
    Calculate the max value
    Return ratio of values
    '''
    #Calculate the max
    maxval = data.iloc[:,0].max()

    #Calculate the average using numerical integration
    dvals = data.iloc[:,0].to_numpy()
    timediff = data.index.to_series().diff() #Convert to series then use diff
    timediff_min = (timediff[1:].to_numpy().astype(float))/(60*(10**9)) #60 x 10^9 to convert from nanosec
    dmins = np.cumsum(timediff_min) #Minutes past starting time
    dmins = np.insert(dmins,0,0)
    dataintegral = np.trapz(dvals,dmins)
    dave = dataintegral/dmins[-1] #Last value should be total time period
    
    #Return the ratio
    return dave/maxval
    

def check_windsp_withdir(wind_speed,wind_direction):
    ''' 
    Check that wind speed is consistent with wind direction.
    Flag speed values suspicious if unchanging at zero wind 
    with wind direction changing.

    Inputs
        wind_speed - numpy array of speeds
        wind_direction - numpy array of directions
        lengths of arrays must match
    Output
        flags - array of flags (0,1)
    '''
    #Calculate the differences between array values
    wsdiff = np.diff(wind_speed)
    wddiff = np.diff(wind_direction)

    #Identify suspicious sections: flat ws slope, changing dir
    slope_compare = np.zeros(len(wsdiff))
    slope_compare[(wsdiff == 0) & (wddiff != 0)] = 1 

    #Loop through values assigning flags
    flags = [0]*len(wind_speed)
    counter = 0
    for slope in slope_compare:
        #Sum adjacent points to identify when points are both 0
        valsum = wind_speed[counter] + wind_speed[counter + 1]
        if (slope > 0) and (valsum == 0):
            flags[counter] = 1
            flags[counter + 1] = 1
        
        counter = counter + 1

    return flags


def check_winddir_withsp(wind_speed,wind_direction):
    '''
    Evaluate direction data
    Any flatlining associated with wind speed > 0 is suspicious.
    Inputs
        wind_speed - numpy array of speeds
        wind_direction - numpy array of directions
        lengths of arrays must match
    Output
        flags - array of flags (0,1)
    '''
    #Calculate slopes between direction values
    wddiff = np.diff(wind_direction)

    #Check areas where wind direction slope is zero against wind speed
    flags = [0]*len(wind_speed)
    counter = 0
    for slope in wddiff:
        #Add adjacent wind speed values to see if both > 0
        valsum = wind_speed[counter] + wind_speed[counter + 1]
        if (slope == 0) & (valsum > 0):
            flags[counter] = 1
            flags[counter + 1] = 1
        
        counter = counter + 1

    return flags


#Quick test
if __name__=='__main__':
    pass