'''
Define dataQC class
- Objects can have multiple ranges describing good, suspicious values
- Where suspicious and good ranges overlap, data will be classified as good
- **rates and flat must be in units of min (for now)
- **each method takes a pandas df with values of interest in col 1 and datetimes col 0
- **each method returns an numpy array of flags for each value
'''

import numpy as np
import pandas as pd

class dataqc:
    '''
    dataqc class:
    Contains QC settings and methods
    '''
    def __init__(self,typename,goodvals,susvals,ignore):
        '''
        Create a new data QC object
        Input
        - typename: type of data
        - goodvals: a list with different good range settings
        - susvals: a list with different suspicious range settings 
        '''
        #Load inputs
        self.datatype = typename
        
        self.goodrange = goodvals['range']   #[(x,y),(x2,y2)...]
        self.goodrate = goodvals['rate']   #Units/min
        self.goodflat = goodvals['flat']   #Minutes
        self.susprange = susvals['range']
        self.susprate = susvals['rate']
        self.suspflat = susvals['flat']
        self.ignore = ignore #Values where flags are removed post analysis

    def _check_range_(self,datavals,flags,minval,maxval,rangetype):
        '''
        "Private" method to check values for a given range
        Inputs
            - datavals: numpy array of data values
            - flags: current numpy array of flags
            - max and min values for range
            - rangetype = 'good' or 'suspicious' 
        Returns
            - np array of flags for each value
        '''
        ranges = {'good':0,'suspicious':1}
        flags[(datavals >= minval) & (datavals <= maxval)] = ranges[rangetype] 

        return flags
        
    
    def check_range(self,data):
        '''
        Check data against all good and suspicious ranges
        Input
        - data: pandas Series
        Returns
        List of flags associated with data values
        '''

        dvals = data.to_numpy()
        flags = np.ones(len(dvals),dtype=np.int8)*2 #Set all flags to 2 (bad)

        #Check suspicious first so that good range will override
        for valrange in self.susprange:
            flags = self._check_range_(dvals,flags,valrange[0],valrange[1],'suspicious')
        
        for valrange in self.goodrange:
            flags = self._check_range_(dvals,flags,valrange[0],valrange[1],'good')

        #Clear flags associated with ignore values
        for ignoreval in self.ignore['range']:
            flags[dvals==ignoreval] = 0
        
        return flags

    def check_rate(self,data):
        '''
        Check data change of rate
        Input
        - data: pandas df with first column values
        
        Returns
        List of flags associated with data values
        '''
        #Calculate rates of change between points (units/min)
        dvals = data.to_numpy()
        valdiff = np.diff(dvals)
        timediff = data.index.to_series().diff() #Convert to series then use diff
        timediff_min = (timediff[1:].to_numpy().astype(float))/(60*(10**9)) #60 x 10^9 to convert from nanosec
        dataslopes = valdiff/timediff_min

        #Determine if different rates are good, suspicious, or bad
        #Check suspicious first so that good range will override
        rateflags = np.ones(len(dataslopes),dtype=np.int8)*2 #Set all flags to 2 (bad)
        for valrange in self.susprate:
            rateflags = self._check_range_(dataslopes,rateflags,valrange[0],valrange[1],'suspicious')
        
        for valrange in self.goodrate:
            rateflags = self._check_range_(dataslopes,rateflags,valrange[0],valrange[1],'good')

        #Flag points based on rate flags
        flags = []
        flagcalc = {0:0,1:1,2:1,3:2,4:2} #Truth table for flag1 + flag2
        for n in range(len(rateflags)-1):
            flags.append(flagcalc[rateflags[n]+rateflags[n+1]])
        #Endpoints
        flags.insert(0,rateflags[0])
        flags.append(rateflags[-1])

        #Clear flags associated with ignore values
        flags = np.array(flags)
        for ignoreval in self.ignore['rate']:
            flags[dvals==ignoreval] = 0
        
        return flags

    def check_flat(self,data):
        '''
        Check input data for excessive flatlining
        Input
        - data: pandas df with first column values
        
        Returns
        List of flags associated with data values
        '''
        #Calculate rates of change between points (units/min)
        dvals = data.to_numpy()
        timediff = data.index.to_series().diff() #Convert to series then use diff
        timediff_min = (timediff[1:].to_numpy().astype(float))/(60*(10**9)) #60 x 10^9 to convert from nanosec
        valdiff = np.diff(dvals)
        
        #Create a list of flags where slopes == 0
        slopeflags = (valdiff==0)*1

        #Combine flags with timediff to isolate times where flat
        timediff = timediff_min*slopeflags

        #Extract the times associated with each flat section
        flatgroups = []
        counter = 0
        oldtime = 0
        for timestep in timediff:
            if (timestep!=0) and (oldtime==0):
                '''
                Starts a section of flat data
                '''
                flatgroups.append(timestep)

            elif (timestep!=0) and (oldtime!=0):
                '''
                Continue adding times to section of flat
                '''
                flatgroups[counter]=flatgroups[counter]+timestep
                
            elif (timestep==0) and (oldtime!=0):
                '''
                Indicates the end of a section
                '''
                counter = counter+1

            oldtime = timestep

        #Check the flatgroups for good, bad, suspicious
        flatgroups = np.array(flatgroups)
        groupflags = np.ones(len(flatgroups),dtype=np.int8)*2 #Set all flags to 2 (bad)
        for valrange in self.suspflat:
            groupflags = self._check_range_(flatgroups,groupflags,valrange[0],valrange[1],'suspicious')
        
        for valrange in self.goodflat:
            groupflags = self._check_range_(flatgroups,groupflags,valrange[0],valrange[1],'good')

        #Update slopeflags to match flag group
        oldflag = 0
        slopeflagsnew = []
        counter = 0
        for flag in slopeflags:

            if (flag!=1) and (oldflag==1):
                '''
                Indicates the end of a flag section
                '''
                counter = counter + 1
            
            if flag==1:
                slopeflagsnew.append(flag*groupflags[counter])
            else:
                slopeflagsnew.append(0)

            oldflag = flag

        #Finally: assign point flags based on slope flags
        flags = []
        for n in range(len(slopeflagsnew)-1):
            flags.append(max(slopeflagsnew[n],slopeflagsnew[n+1]))
        #Endpoints
        flags.insert(0,slopeflagsnew[0])
        flags.append(slopeflagsnew[-1])

        #Clear flags associated with ignore values
        flags = np.array(flags)
        for ignoreval in self.ignore['flat']:
            flags[dvals==ignoreval] = 0
 
        return flags




