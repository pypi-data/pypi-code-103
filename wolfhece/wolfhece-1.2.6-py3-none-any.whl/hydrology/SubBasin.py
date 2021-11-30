import sys
import numpy as np
import csv
import os

from numpy.ma.core import append, shape
from numpy.testing._private.utils import suppress_warnings
import constant as cst
import math
import time as time_mod
import matplotlib.pyplot as plt
import scipy.stats as stats             #pip install Scipy
import datetime                         # module which contains objects treating dates
from matplotlib.font_manager import FontProperties
from dbfread import DBF

if not '_' in globals()['__builtins__']: #Test de la présence de la fonction de traduction i18n "gettext" et définition le cas échéant pour ne pas créer d'erreur d'exécution
    import gettext
    _=gettext.gettext

from . import plot_hydrology as ph
from . import data_treatment as datt
from . import read as rd

from ..wolf_array import *
from ..PyParams import*

## TO DO:
# - add the arguments _dateBegin, _dateEnd and _deltaT as optional
#       -> In this way, the init of these variable can be done by reading the rain, evap or outflow file if not already init

class SubBasin:

    def __init__(self, _dateBegin, _dateEnd, _deltaT, _model,_workingDir, _hyeto={}, _x=0.0, _y=0.0, 
                 _iD_interiorPoint=1,_idSorted=1, name=None, readHydro=True, _tz=0):
        if(name is None):
            self.name = 'ss '+ str(_iD_interiorPoint)
        else:           
            self.name = name
        self.iD = 'ss'+str(_iD_interiorPoint)
        self.iDSorted = _idSorted
        self.x = _x
        self.y = _y
        self.haveInlets = False
        self.alreadyUsed = False    # //
        self.isLeveled = False
        ## Time array containing all the timestamps
        # @var time timestamps array of dimension equal to rain and evap (or 1 element more than myHydro so far (VHM but not UH)).
        self.time = []

        self.dateBegin = _dateBegin     # Must be in GMT+0 !!!
        self.dateEnd = _dateEnd         # Must be in GMT+0 !!!
        self.deltaT = _deltaT
        # @var timezone in GMT saved to converted all computed or read data so that all data are expressed in GMT+0
        self.tz = _tz 
        self.model = _model
        
        
        self.treated = False        # //
        self.myLevel = 1
        self.fileNameRead = _workingDir # //
        self.fileNameWrite = self.fileNameRead  # TO DO !!!!!!!!
        # self.intersectIndex = 0

        ## Dictionary containing all the objects Catchment:
        ## @var myHydro an array whose dimensions depends on the model chosen: 
        #  - Unit hydrographs and Linear reservoir models : $1\times n$ elements
        #  - VHM model : $3\times n$ elements:
        #                myHydro[i][0] : overland flow
        #                myHydro[i][1] : interflow
        #                myHydro[i][2] : baseflow
        #  @unit $[\si{m}^3/\si{s}}]$
        self.myHydro = []                           # [m^3/s] Hydro of the subbasin only

        self.intletsObj = []
        self.inlets = []
        self.inletsRaw = [] 
        self.downstreamObj = None

        ## @var outFlow 
        # Hydro of the hydrological subbasin. Combined with the potentiel upstream hydros. Consider timeDelay so that time is at 0
        # @unit $[\si{m}^3/\si{s}}]$
        self.outFlow = []                           # [m^3/s] Hydro of the hydrological subbasin. Combined with the potentiel upstream hydros. Consider timeDelay so that time is at 0

        self.outFlowRaw = []                        # [m^3/s]
        # Hyeto
        self.myHyetoDict = {}
        self.myRain = []                            # [mm/h]   Caution in the difference of units in rain !!!!!!
        self.rain = []                              # [m^3/h]  Caution in the difference of units in rain !!!!!!
        # Evapotranspiration
        self.myEvap = []                            # [mm/h]
        self.evap = []                              # [mm/h]
        # Temperature
        self.myTemp = []
        # Outflow converted in hystograph
        self.hydrograph = []        # //
        # self.hystograph = []

        # Main subbasin characteristics
        self.mainCharactDict = {}                   # Dictionnary with the main characteristics of the subbasin

        # Further information
        self.surfaceDrained = 0.0                   # [km^2]
        surfaceDrainedHydro = 0.0                   # [km^2]
        self.timeDelay = 0.0                        # [km^2] 






        # Verification of the unicity of the time array 
        # Load all the hydrographs of the sub-basins
        if(self.model==cst.measures):
            readHydro=False
        # Get the main characteristics of the subbasin. If the hydro can be read, so be the main characteristics
        if(readHydro):
            self.get_myMainCharacteristics(_workingDir)
        if(readHydro):
            timeTest, self.myHydro = self.get_hydro(self.iDSorted, _workingDir, tzDelta=datetime.timedelta(hours=self.tz))
            if(self.time==[]):
                self.time = timeTest
            else:
                if not(np.array_equal(timeTest,self.time)):
                    print('ERROR: Time array not the same! Please check your answers.')
                    sys.exit()  


        

        print('Hello SubBasin!')




    def change_haveInlets(self):
        "This procedure only increment the number of inlets of a subbasin"
        self.haveInlets = True


    def get_hydro(self, iDSorted, workingDir, fileNames=None, tzDelta=datetime.timedelta(hours=0)):
        if(self.model==cst.tom_UH):
            print("Reading the Unit Hydrograph outlets...")

            # initialisation of the fileNames
            if(fileNames==None):
                subBasinName = 'Subbasin_' + str(iDSorted) + '/'
                typeOfFileName = 'simul_of.txt'
                fileName = workingDir + subBasinName + typeOfFileName
                file_exists = os.path.exists(fileName)
                if(not(file_exists)):
                    typeOfFileName = 'simul_net_trans_rain.txt'
                    fileName = workingDir + subBasinName + typeOfFileName
                    file_exists = os.path.exists(fileName)
                    if(file_exists):
                        print("ERROR : the file simul_net_trans_rain.txt is not used yet in this version! Please check version of the code before 05/11/2021 !")
                        sys.exit()
                    else:
                        print("ERROR : the hydro file is not present here!")
                        sys.exit()
            else:
                # The file can only be a string or a list with 1 string
                if(type(fileNames)==str):      
                    fileName = workingDir + fileNames[0]
                elif(type(fileNames)==list and len(fileNames)!=1):
                    fileName = workingDir + fileNames
                else:
                    print("ERROR: Expecting only 1 file name for UH model!")
                    sys.exit()

            # Reading the hydro output file
            with open(fileName, newline = '') as fileID:                                                                                          
                data_reader = csv.reader(fileID, delimiter='\t')
                list_data = []
                i = 0
                for raw in data_reader:
                    if i>1:
                        list_data.append(raw)
                    i += 1
            matrixData = np.array(list_data).astype("float")
            timeArray = np.zeros(len(matrixData)+1)                 # +1 as the time array is not one element more than the outlet in UH
            outFlow = np.zeros(len(matrixData))

            secondsInDay = 24*60*60
            prevDate = datetime.datetime(year=int(matrixData[0][2]), month=int(matrixData[0][1]), day=int(matrixData[0][0]), hour=int(matrixData[0][3]), minute=int(matrixData[0][4]), second=int(matrixData[0][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
            prevDate -= tzDelta
            if(self.dateBegin!=prevDate):
                print("ERROR: The first date in hydro data does not coincide with the one expected!")
                sys.exit()
            outFlow[0] = matrixData[0][6]
            timeArray[0] = datetime.datetime.timestamp(prevDate)
            # Caution!! -1 is here because the size of hydros in UH is the same as rain (not the case in VHM)
            nbData = len(matrixData)
            
            for i in range(1,nbData):
                currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), minute=int(matrixData[i][4]), second=int(matrixData[i][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
                currDate -= tzDelta
                prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), minute=int(matrixData[i-1][4]), second=int(matrixData[i-1][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
                prevDate -= tzDelta
                diffDate = currDate - prevDate
                diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
                timeArray[i] = datetime.datetime.timestamp(currDate)
                # timeArray[i] = timeArray[i-1] + diffTimeInSeconds
                outFlow[i] = matrixData[i][6]
            timeArray[-1] = timeArray[-2] + diffTimeInSeconds
            # The last date is not taken into account in hydro as the last date rain and evap is needed for implicit simulations
            if(self.dateEnd-diffDate!=currDate):
                print("ERROR: The last date in hydro data does not coincide with the one expected!")
                sys.exit()
            if(self.deltaT!=diffTimeInSeconds):
                print("ERROR: The last timestep in hydro data does not coincide with the one expected!")
                sys.exit()
            # Save time array if it does not exist yet
            # Otherwise, check the consistency of the array with the time array of the object
            if(self.time==[]):
                self.time=timeArray
            elif(self.time!=timeArray):
                print("ERROR: the dates read are not consitent with the dates already recored in this subbasin!")
                sys.exit()

        elif(self.model==cst.tom_2layers_linIF):
            # For this model, there are 3 different layers to read.

            print("Reading the 2 outlet files...")
            matrixData = []

            # Reading the overland flow file and time
            if(fileNames==None):
                subBasinName = workingDir + 'Subbasin_' + str(iDSorted) + '/simul_'
                fileName = subBasinName + "of.txt"
            else:
                if(len(fileNames)!=2):
                    print("ERROR: Expecting 2 file names for VHM model!")
                    sys.exit()
                fileName = workingDir + fileNames[0]

            with open(fileName, newline = '') as fileID:                                                                                          
                data_reader = csv.reader(fileID, delimiter='\t')
                list_data = []
                i=0
                for raw in data_reader:
                    if i>1:
                        list_data.append(raw)
                    i += 1 
            matrixData = np.array(list_data).astype("float")
            timeArray = np.zeros(len(matrixData)+1)
            # Init of the outflow array
            outFlow = np.zeros((len(matrixData),2))

            secondsInDay = 24*60*60
            prevDate = datetime.datetime(year=int(matrixData[0][2]), month=int(matrixData[0][1]), day=int(matrixData[0][0]), hour=int(matrixData[0][3]), minute=int(matrixData[0][4]), second=int(matrixData[0][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
            prevDate -= tzDelta
            if(self.dateBegin!=prevDate):
                print("ERROR: The first date in hydro data does not coincide with the one expected!")
                sys.exit()
            timeArray[0] = datetime.datetime.timestamp(prevDate)
            outFlow[0][0] = matrixData[0][6]
            for i in range(1,len(matrixData)):
                currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), minute=int(matrixData[i][4]), second=int(matrixData[i][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
                currDate -= tzDelta
                prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), minute=int(matrixData[i-1][4]), second=int(matrixData[i-1][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
                prevDate -= tzDelta
                diffDate = currDate - prevDate
                diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
                timeArray[i] = datetime.datetime.timestamp(currDate)
                # timeArray[i] = timeArray[i-1] + diffTimeInSeconds
                outFlow[i][0] = matrixData[i][6]
            timeArray[-1] = timeArray[-2] + diffTimeInSeconds
            # The last date is not taken into account in hydro as the last date rain and evap is needed for implicit simulations
            if(self.dateEnd-diffDate!=currDate):
                print("ERROR: The last date in hydro data does not coincide with the one expected!")
                sys.exit()
            if(self.deltaT!=diffTimeInSeconds):
                print("ERROR: The last timestep in hydro data does not coincide with the one expected!")
                sys.exit()
            # Save time array if it does not exist yet
            # Otherwise, check the consistency of the array with the time array of the object
            if(self.time==[]):
                self.time=timeArray
            elif(self.time!=timeArray):
                print("ERROR: the dates read are not consitent with the dates already recored in this subbasin!")
                sys.exit()

            # Reading the interflow file
            matrixData = []
            if(fileNames==None):
                fileName = subBasinName + "if.txt"
            else:
                fileName = workingDir + fileNames[1]

            with open(fileName, newline = '') as fileID:                                                                                          
                data_reader = csv.reader(fileID, delimiter='\t')
                list_data = []
                i=0
                for raw in data_reader:
                    if i>1:
                        list_data.append(raw)
                    i += 1 
            matrixData = np.array(list_data).astype("float")

            outFlow[0][1] = matrixData[0][6]*self.surfaceDrained/3.6
            for i in range(1,len(matrixData)):
                outFlow[i][1] = matrixData[i][6]*self.surfaceDrained/3.6


        elif(self.model==cst.tom_VHM):
            print("TO DO: adapt the timezone !!!")
            sys.exit()
            # For this model, there are 3 different layers to read.

            print("Reading the 3 VHM outlet files...")
            matrixData = []

            # Reading the overland flow file and time
            if(fileNames==None):
                subBasinName = workingDir + 'Subbasin_' + str(iDSorted) + '/simul_'
                fileName = subBasinName + "of.txt"
            else:
                if(len(fileNames)!=3):
                    print("ERROR: Expecting 3 file names for VHM model!")
                    sys.exit()
                fileName = workingDir + fileNames[0]

            with open(fileName, newline = '') as fileID:                                                                                          
                data_reader = csv.reader(fileID, delimiter='\t')
                list_data = []
                i=0
                for raw in data_reader:
                    if i>1:
                        list_data.append(raw)
                    i += 1 
            matrixData = np.array(list_data).astype("float")
            timeArray = np.zeros(len(matrixData)+1)
            # Init of the outflow array
            outFlow = np.zeros((len(matrixData),3))

            secondsInDay = 24*60*60
            prevDate = datetime.datetime(year=int(matrixData[0][2]), month=int(matrixData[0][1]), day=int(matrixData[0][0]), hour=int(matrixData[0][3]), minute=int(matrixData[0][4]), second=int(matrixData[0][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
            if(self.dateBegin!=prevDate):
                print("ERROR: The first date in hydro data does not coincide with the one expected!")
                sys.exit()
            timeArray[0] = datetime.datetime.timestamp(prevDate)
            outFlow[0][0] = matrixData[0][6]*self.surfaceDrained/3.6
            for i in range(1,len(matrixData)):
                currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), minute=int(matrixData[i][4]), second=int(matrixData[i][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
                prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), minute=int(matrixData[i-1][4]), second=int(matrixData[i-1][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
                diffDate = currDate - prevDate
                diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
                timeArray[i] = datetime.datetime.timestamp(currDate)
                # timeArray[i] = timeArray[i-1] + diffTimeInSeconds
                outFlow[i][0] = matrixData[i][6]*self.surfaceDrained/3.6
            timeArray[-1] = timeArray[-2] + diffTimeInSeconds
            # The last date is not taken into account in hydro as the last date rain and evap is needed for implicit simulations
            if(self.dateEnd-diffDate!=currDate):
                print("ERROR: The last date in hydro data does not coincide with the one expected!")
                sys.exit()
            if(self.deltaT!=diffTimeInSeconds):
                print("ERROR: The last timestep in hydro data does not coincide with the one expected!")
                sys.exit()
            # Save time array if it does not exist yet
            # Otherwise, check the consistency of the array with the time array of the object
            if(self.time==[]):
                self.time=timeArray
            elif(self.time!=timeArray):
                print("ERROR: the dates read are not consitent with the dates already recored in this subbasin!")
                sys.exit()

            # Reading the interflow file
            matrixData = []
            if(fileNames==None):
                fileName = subBasinName + "if.txt"
            else:
                fileName = workingDir + fileNames[1]

            with open(fileName, newline = '') as fileID:                                                                                          
                data_reader = csv.reader(fileID, delimiter='\t')
                list_data = []
                i=0
                for raw in data_reader:
                    if i>1:
                        list_data.append(raw)
                    i += 1 
            matrixData = np.array(list_data).astype("float")

            outFlow[0][1] = matrixData[0][6]*self.surfaceDrained/3.6
            for i in range(1,len(matrixData)):
                outFlow[i][1] = matrixData[i][6]*self.surfaceDrained/3.6

            # Reading the baseflow file
            matrixData = []
            if(fileNames==None):
                fileName = subBasinName + "bf.txt"
            else:
                fileName = workingDir + fileNames[2]

            with open(fileName, newline = '') as fileID:                                                                                          
                data_reader = csv.reader(fileID, delimiter='\t')
                list_data = []
                i=0
                for raw in data_reader:
                    if i>1:
                        list_data.append(raw)
                    i += 1 
            matrixData = np.array(list_data).astype("float")

            outFlow[0][2] = matrixData[0][6]*self.surfaceDrained/3.6
            for i in range(1,len(matrixData)):
                outFlow[i][2] = matrixData[i][6]*self.surfaceDrained/3.6


        elif(self.model==cst.tom_GR4):
            print("TO DO: adapt the timezone !!!")
            sys.exit()
            # For this model, there is only 1 output to consider.

            print("Reading the 1 outlet file ...")
            matrixData = []

            # Reading the overland flow file and time
            if(fileNames==None):
                subBasinName = workingDir + 'Subbasin_' + str(iDSorted) + '/simul_'
                fileName = subBasinName + "GR4_out.txt"
            else:
                # The file can only be a string or a list with 1 string
                if(type(fileNames)==str):      
                    fileName = workingDir + fileNames[0]
                elif(type(fileNames)==list and len(fileNames)==1):
                    fileName = workingDir + fileNames
                else:
                    print("ERROR: Expecting only 1 file name for UH model!")
                    sys.exit()

            with open(fileName, newline = '') as fileID:                                                                                          
                data_reader = csv.reader(fileID, delimiter='\t')
                list_data = []
                i=0
                for raw in data_reader:
                    if i>1:
                        list_data.append(raw)
                    i += 1 
            matrixData = np.array(list_data).astype("float")
            timeArray = np.zeros(len(matrixData)+1)
            # Init of the outflow array
            outFlow = np.zeros((len(matrixData),1))

            secondsInDay = 24*60*60
            prevDate = datetime.datetime(year=int(matrixData[0][2]), month=int(matrixData[0][1]), day=int(matrixData[0][0]), hour=int(matrixData[0][3]), minute=int(matrixData[0][4]), second=int(matrixData[0][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
            if(self.dateBegin!=prevDate):
                print("ERROR: The first date in hydro data does not coincide with the one expected!")
                sys.exit()
            timeArray[0] = datetime.datetime.timestamp(prevDate)
            outFlow[0][0] = matrixData[0][6]*self.surfaceDrained/3.6
            for i in range(1,len(matrixData)):
                currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), minute=int(matrixData[i][4]), second=int(matrixData[i][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
                prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), minute=int(matrixData[i-1][4]), second=int(matrixData[i-1][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
                diffDate = currDate - prevDate
                diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
                timeArray[i] = datetime.datetime.timestamp(currDate)
                # timeArray[i] = timeArray[i-1] + diffTimeInSeconds
                outFlow[i][0] = matrixData[i][6]*self.surfaceDrained/3.6
            timeArray[-1] = timeArray[-2] + diffTimeInSeconds
            # The last date is not taken into account in hydro as the last date rain and evap is needed for implicit simulations
            if(self.dateEnd-diffDate!=currDate):
                print("ERROR: The last date in hydro data does not coincide with the one expected!")
                sys.exit()
            if(self.deltaT!=diffTimeInSeconds):
                print("ERROR: The last timestep in hydro data does not coincide with the one expected!")
                sys.exit()
            # Save time array if it does not exist yet
            # Otherwise, check the consistency of the array with the time array of the object
            if(self.time==[]):
                self.time=timeArray
            elif(self.time!=timeArray):
                print("ERROR: the dates read are not consitent with the dates already recored in this subbasin!")
                sys.exit()

        elif(self.model==cst.measures):
            print("Reading the measurements outlet file...")
            if(type(fileNames)!=str):
                print("ERROR: Expecting only 1 file name for measurements!")
                sys.exit()
            fileName = workingDir + fileNames
            nbCl = 0
            with open(fileName, newline = '') as fileID:                                                                                          
                data_reader = csv.reader(fileID, delimiter=' ',skipinitialspace=True)
                list_data = []
                i=0
                for raw in data_reader:
                    if i>3:
                        list_data.append(raw[0:nbCl])
                    if i==2:
                        nbCl = int(raw[0])
                    i += 1
 
            matrixData = np.array(list_data).astype("float")
            # Init of the outflow array
            timeInterval = self.dateEnd-self.dateBegin
            outFlow = np.zeros(int(timeInterval.total_seconds()/self.deltaT))
            timeArray = np.zeros(int(timeInterval.total_seconds()/self.deltaT)+1)
          
            # From the measurements file, we will only read the desired data and save it in outflow
            prevDate = datetime.datetime(year=int(matrixData[0][2]), month=int(matrixData[0][1]), day=int(matrixData[0][0]), hour=int(matrixData[0][3]), tzinfo=datetime.timezone.utc)
            prevDate -= tzDelta
            index = 0
            add1Hour = datetime.timedelta(hours=1)
            secondsInDay = 24*60*60

            # Verification
            if(datetime.datetime.timestamp(prevDate)>datetime.datetime.timestamp(self.dateBegin)):
                print("ERROR: the first hydro data element is posterior to dateBegin!")
                sys.exit()

            if(nbCl==5):
                # Caution : the index of the loop start at 24 because the timestamp function 
                # does not work until the 2/01/1970 at 03:00:00. => Je ne sais pas pourquoi ?!
                for i in range(25,len(matrixData)):
                    # The hours are written in the file in [1,24] instead of [0,23]. Conversion below:
                    if(int(matrixData[i][3])==24):
                        currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=23, tzinfo=datetime.timezone.utc) + add1Hour
                    else:
                        currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), tzinfo=datetime.timezone.utc)
                    currDate -= tzDelta
                    if(int(matrixData[i-1][3])==24):
                        prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=23, tzinfo=datetime.timezone.utc) + add1Hour
                    else:
                        prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), tzinfo=datetime.timezone.utc)
                    prevDate -= tzDelta
                    # Start at dateBegin and go to the element before dateEnd. Because the last date is needed for rain and evap in implicit simulations.
                    if(datetime.datetime.timestamp(currDate)>=datetime.datetime.timestamp(self.dateBegin) and \
                    datetime.datetime.timestamp(currDate)<datetime.datetime.timestamp(self.dateEnd)):
                        outFlow[index] = matrixData[i][4]
                        diffDate = currDate - prevDate
                        diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
                        timeArray[index] = datetime.datetime.timestamp(currDate)
                        # timeArray[index] = timeArray[index-1] + diffTimeInSeconds
                        index += 1
            elif(nbCl==7):
                for i in range(len(matrixData)):
                    # The hours are written in the file in [1,24] instead of [0,23]. Conversion below:                    
                    currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), minute=int(matrixData[i][4]), second=int(matrixData[i][5]),tzinfo=datetime.timezone.utc)
                    currDate -= tzDelta
                    prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), minute=int(matrixData[i-1][4]), second=int(matrixData[i-1][5]),tzinfo=datetime.timezone.utc)
                    prevDate -= tzDelta
                    # Start at dateBegin and go to the element before dateEnd. Because the last date is needed for rain and evap in implicit simulations.
                    if(datetime.datetime.timestamp(currDate)>=datetime.datetime.timestamp(self.dateBegin) and \
                    datetime.datetime.timestamp(currDate)<datetime.datetime.timestamp(self.dateEnd)):
                        if(matrixData[i][6]<0):
                            outFlow[index] = 0.0
                        else:
                            outFlow[index] = matrixData[i][6]
                        outFlow[index] = matrixData[i][6]
                        diffDate = currDate - prevDate
                        diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
                        timeArray[index] = datetime.datetime.timestamp(currDate)
                        # timeArray[index] = timeArray[index-1] + diffTimeInSeconds
                        index += 1
            # The last date is not taken into account in hydro as the last date rain and evap is needed for implicit simulations
            diffDate = currDate - prevDate
            # Add the last element in the time matrix as its size is 1 element bigger than outlet
            timeArray[-1] = timeArray[-2] + diffTimeInSeconds
            if(self.deltaT!=diffDate.seconds):
                print("ERROR: The last timestep in hydro data does not coincide with the one expected!")
                sys.exit()
            # Save time array if it does not exist yet
            # Otherwise, check the consistency of the array with the time array of the object
            if(self.time==[]):
                self.time=timeArray
            elif(self.time!=timeArray):
                print("ERROR: the dates read are not consitent with the dates already recored in this subbasin!")
                sys.exit()
        
        return timeArray, outFlow


    def get_outFlow_noDelay(self):
        '''
        This function returns the total outlet of the basin and considers t0=0 at the outlet of the 
        subbasin without considering timeDelay (the time of the real outlet of the whole potential catchment)
        '''

        tmpHydro = np.zeros(len(self.outFlow))
        index = math.floor(self.timeDelay/self.deltaT)
        if(index==0): 
            tmpHydro = self.outFlow
        elif(index<len(self.outFlow)):
            tmpHydro[:-index] = self.outFlow[index:]
        else:
            print("ERROR: the simulation time is not long enough for this subbasin to be taken into account")
            sys.exit()


        return tmpHydro

    
    def get_outFlowRaw_noDelay(self):
        '''
        This function returns the total raw outlet of the basin and considers t0=0 at the outlet of the 
        subbasin without considering timeDelay (the time of the real outlet of the whole potential catchment)
        '''

        tmpHydro = np.zeros(len(self.outFlowRaw))
        index = math.floor(self.timeDelay/self.deltaT)
        if(index==0): 
            tmpHydro = self.outFlowRaw
        elif(index<len(self.outFlowRaw)):
            tmpHydro[:-index] = self.outFlowRaw[index:]
        else:
            print("ERROR: the simulation time is not long enough for this subbasin to be taken into account")
            sys.exit()


        return tmpHydro


    def add_name(self, myName):
        "this function add a name to the subasin"
        self.name = myName


    def increment_level(self):
        "This procedure increment the level in the Topo dictionary"
        self.myLevel += 1


    def set_level(self, level):
        self.myLevel = level


    def add_inlet(self, toPoint):
        "This procedure link the inlets to the object"
        self.intletsObj.append(toPoint)


    def add_downstreamObj(self, toPoint):
        "This procedure link the downstream element to the object"
        self.downstreamObj = toPoint


    def compute_hydro(self):
        """This procedure computes the total hydrograph and raw hydrograph of subbasin

            The total hydrograph $q_{tot} is obtained with the formula:
            \f[
            q_{tot} = \sum q_{\text{inlets}} + q_{\text{me}}$
            \f]
            , with $q_{\text{me}}$ the hydrograph of the subbasin alone.

            Internal variable changed: outFlowRaw, outFlow, inletsRaw
            CAUTION: Discussion about the ceil or the floor for the timeDelay indice!!!
        """
        # Sum all the inlets hydrographs
        self.sum_inlets()
        if(self.model==cst.tom_UH or self.model==cst.measures or self.model==cst.tom_GR4):
            tmpHydro = np.zeros(len(self.myHydro))
            index = math.floor(self.timeDelay/self.deltaT)
            if(index==0): 
                if(self.model==cst.tom_GR4):
                    tmpHydro = self.myHydro[:,0]
                else:               
                    tmpHydro = self.myHydro
            elif(index<len(self.myHydro)):
                tmpHydro[index:] = self.myHydro[:-index]
            else:
                print("ERROR: the simulation time is not long enough for this subbasin to be taken into account")
                sys.exit()
            # Raw hydrograph
            self.outFlowRaw = self.inletsRaw + tmpHydro
            # Real hydrograph
            self.outFlow  = self.inlets + tmpHydro
        elif(self.model==cst.tom_VHM or self.model==cst.tom_2layers_linIF):

            tmpOutFlow = np.zeros(len(self.inlets))
            index = math.floor(self.timeDelay/self.deltaT)
            if(index==0):
                tmpOutFlow = np.sum(self.myHydro,1)
            elif(index<len(self.myHydro)):
                tmpOutFlow[index:] = np.sum(self.myHydro[:-index],1)
            else:
                print("ERROR: the simulation time is not long enough for this subbasin to be taken into account")
                sys.exit()

            # Raw hydrograph
            self.outFlowRaw = np.zeros(len(tmpOutFlow))      
            self.outFlowRaw = self.inletsRaw + tmpOutFlow
            # for i in range(len(self.myHydro)):
            #     self.outFlowRaw[i] = self.inletsRaw[i] + np.sum(self.myHydro[i])

            # Real hydrograph
            self.outFlow = np.zeros(len(self.myHydro))
            self.outFlow = self.inlets + tmpOutFlow
            # for i in range(len(self.myHydro)):
            #     self.outFlow[i] = self.inlets[i] + np.sum(self.myHydro[i])
            


    def sum_inlets(self):
        """ Sum all the inlet hydrographs of a subbasin. Return an array of zeros otherwise.

            Internal variable changed: self.inlets, self.inletsRaw
        """
        if(self.haveInlets):
            self.inlets = self.intletsObj[0].outFlow.copy()
            self.inletsRaw = self.intletsObj[0].outFlowRaw.copy()
            for i in range(1,len(self.intletsObj)):
                self.inlets += self.intletsObj[i].outFlow
                self.inletsRaw += self.intletsObj[i].outFlowRaw
        else:
            self.inlets = np.zeros(len(self.myHydro))
            self.inletsRaw = np.zeros(len(self.myHydro))


    def add_rain(self, workingDir, fileName=None, tzDelta=datetime.timedelta(hours=0)):
        """ This procedure 
            - reads: the time, rain in the rain file
            - saves: the rain of the subbasin, sum of the rain's inlets
            - returns: the time array read.
            - Variables modified: self.rain, self.myRain
        """
        # Reading and saving the rain's basin
        if(fileName==None):
            fileName = 'Subbasin_'+str(self.iDSorted)+'/simul_lumped_rain.txt'
        
        with open(workingDir+fileName, newline = '') as fileID2:                                                                                          
            data_reader = csv.reader(fileID2, delimiter='\t')
            list_data = []
            i=0
            for raw in data_reader:
                if i>1:
                    list_data.append(raw)
                i += 1 
        matrixData = np.array(list_data).astype("float")
        rain = np.zeros(len(matrixData))
        time = np.zeros(len(matrixData))

        secondsInDay = 24*60*60
        prevDate = datetime.datetime(year=int(matrixData[0][2]), month=int(matrixData[0][1]), day=int(matrixData[0][0]), hour=int(matrixData[0][3]), minute=int(matrixData[0][4]), second=int(matrixData[0][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
        prevDate -= tzDelta
        if(self.dateBegin!=prevDate):
            print("ERROR: The first date in rain data does not coincide with the one expected!")
            sys.exit()
        time[0] = datetime.datetime.timestamp(prevDate)
        for i in range(1,len(matrixData)):
            currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), minute=int(matrixData[i][4]), second=int(matrixData[i][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
            currDate -= tzDelta
            prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), minute=int(matrixData[i-1][4]), second=int(matrixData[i-1][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
            prevDate -= tzDelta
            diffDate = currDate - prevDate
            diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
            time[i] = datetime.datetime.timestamp(currDate)
            # time[i] = time[i-1] + diffTimeInSeconds
            rain[i] = matrixData[i][6]
        if(self.dateEnd!=currDate):
            print("ERROR: The last date in rain data does not coincide with the one expected!")
            sys.exit()
        if(self.deltaT!=diffTimeInSeconds):
            print("ERROR: The last timestep in rain data does not coincide with the one expected!")
            sys.exit()
        if(self.time==[]):
            self.time=time
        elif not(np.array_equal(time,self.time)):
            print('Time arrays are not the same! Please check your answers.')
            sys.exit()
        self.myRain = rain
        # Unit conversion to [m^3/s]
        rain = rain*10**(-3)*self.surfaceDrained*10**(6)/3600.0
        # Sum of the rain of all the inlets to get the total rain
        for i in range(len(self.intletsObj)):
            rain += self.intletsObj[i].rain
        self.rain = rain

        return time


    def add_evap(self, workingDir, fileName=None, tzDelta=datetime.timedelta(hours=0)):
        """ This procedure 
            - reads: the time, evapotranspiration in the evap file
            - saves: the evapotranspiration of the subbasin, sum of the evapotranspiration's inlets -> to correct with surface of the basin
            - returns: the time array read.
            - Variables modified: self.evap, self.myEvap
        """
        # Reading and saving the evap's basin
        if(fileName==None):
            fileName = 'Subbasin_'+str(self.iDSorted)+'/simul_lumped_evap.txt'
        
        with open(workingDir+fileName, newline = '') as fileID2:                                                                                          
            data_reader = csv.reader(fileID2, delimiter='\t')
            list_data = []
            i=0
            for raw in data_reader:
                if i>1:
                    list_data.append(raw)
                i += 1 
        matrixData = np.array(list_data).astype("float")
        evap = np.zeros(len(matrixData))
        time = np.zeros(len(matrixData))

        secondsInDay = 24*60*60
        prevDate = datetime.datetime(year=int(matrixData[0][2]), month=int(matrixData[0][1]), day=int(matrixData[0][0]), hour=int(matrixData[0][3]), minute=int(matrixData[0][4]), second=int(matrixData[0][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
        prevDate -= tzDelta
        if(self.dateBegin!=prevDate):
            print("ERROR: The first date in evap data does not coincide with the one expected!")
            sys.exit()
        time[0] = datetime.datetime.timestamp(prevDate)
        for i in range(1,len(matrixData)):
            currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), minute=int(matrixData[i][4]), second=int(matrixData[i][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
            currDate -= tzDelta
            prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), minute=int(matrixData[i-1][4]), second=int(matrixData[i-1][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
            prevDate -= tzDelta
            diffDate = currDate - prevDate
            diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
            time[i] = datetime.datetime.timestamp(currDate)
            # time[i] = time[i-1] + diffTimeInSeconds
            evap[i] = matrixData[i][6]
        if(self.dateEnd!=currDate):
            print("ERROR: The last date in evap data does not coincide with the one expected!")
            sys.exit()
        if(self.deltaT!=diffTimeInSeconds):
            print("ERROR: The last timestep in evap data does not coincide with the one expected!")
            sys.exit()
        if(self.time==[]):
            self.time = time
        elif not(np.array_equal(time,self.time)):
            print('Time arrays are not the same! Please check your answers.')
            sys.exit()
        self.myEvap = evap

        # Unit conversion to [m^3/s]
        evap = evap*10**(-3)*self.surfaceDrained*10**(6)/3600.0
        # Sum of the evap of all the inlets to get the total evap
        for i in range(len(self.intletsObj)):
            evap += self.intletsObj[i].evap
        self.evap = evap

        return time


    def add_temp(self, workingDir, fileName=None, tzDelta=datetime.timedelta(hours=0)):
        """ This procedure 
            - reads: the time, mean temperature in a day in the Temp file
            - saves: the temperatures of the subbasin
            - returns: the time array read.
            - Variables modified: self.myTemp
        """
        # Reading and saving the temperature's basin
        if(fileName==None):
            fileName = 'Subbasin_'+str(self.iDSorted)+'/simul_lumped_Temp.txt'
        
        with open(workingDir+fileName, newline = '') as fileID2:                                                                                          
            data_reader = csv.reader(fileID2, delimiter='\t')
            list_data = []
            i=0
            for raw in data_reader:
                if i>1:
                    list_data.append(raw)
                i += 1 
        matrixData = np.array(list_data).astype("float")
        temp = np.zeros(len(matrixData))
        time = np.zeros(len(matrixData))

        secondsInDay = 24*60*60
        prevDate = datetime.datetime(year=int(matrixData[0][2]), month=int(matrixData[0][1]), day=int(matrixData[0][0]), hour=int(matrixData[0][3]), minute=int(matrixData[0][4]), second=int(matrixData[0][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
        prevDate -= tzDelta
        if(self.dateBegin!=prevDate):
            print("ERROR: The first date in temperature data does not coincide with the one expected!")
            sys.exit()
        time[0] = datetime.datetime.timestamp(prevDate)
        for i in range(1,len(matrixData)):
            currDate = datetime.datetime(year=int(matrixData[i][2]), month=int(matrixData[i][1]), day=int(matrixData[i][0]), hour=int(matrixData[i][3]), minute=int(matrixData[i][4]), second=int(matrixData[i][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
            currDate -= tzDelta
            prevDate = datetime.datetime(year=int(matrixData[i-1][2]), month=int(matrixData[i-1][1]), day=int(matrixData[i-1][0]), hour=int(matrixData[i-1][3]), minute=int(matrixData[i-1][4]), second=int(matrixData[i-1][5]),  microsecond=0, tzinfo=datetime.timezone.utc)
            prevDate -= tzDelta
            diffDate = currDate - prevDate
            diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
            time[i] = datetime.datetime.timestamp(currDate)
            # time[i] = time[i-1] + diffTimeInSeconds
            temp[i] = matrixData[i][6]
        if(self.dateEnd!=currDate):
            print("ERROR: The last date in temperature data does not coincide with the one expected!")
            sys.exit()
        if(self.deltaT!=diffTimeInSeconds):
            print("ERROR: The last timestep in temperature data does not coincide with the one expected!")
            sys.exit()
        if(self.time==[]):
            self.time = time
        elif not(np.array_equal(time,self.time)):
            print('Time arrays are not the same! Please check your answers.')
            sys.exit()
        self.myTemp = temp

        return time


    def read_dbfFile(self, fileName):
        dbfDict = DBF(fileName, load=True)
        return dbfDict


    def add_hyeto(self, workingDir, hyetoDict):
        '''Add hyetographs to the subbasin
            TO DO: Adapt the code to find automatically the .dbf files. E.G. when data are read in NetCDF files.
        '''
        fileName = workingDir + 'Subbasin_'+str(self.iDSorted)+'/simul_rain_geom_126.vec.dbf'
        fileName2 = workingDir + 'Subbasin_'+str(self.iDSorted)+'/simul_geom.vec.dbf'

        if(os.path.exists(fileName)):
            dbDict = self.read_dbfFile(fileName)
            for i in range(len(dbDict.records)):
                idHyeto = int(dbDict.records[i]['data'])
                # idMyHyeto = hyetoDict['Ordered To Nb'][idHyeto]
                self.myHyetoDict[idHyeto] = hyetoDict['Hyetos'][idHyeto]
        elif(os.path.exists(fileName2)):
            dbDict = self.read_dbfFile(fileName2)
            for i in range(len(dbDict.records)):
                idHyeto = int(dbDict.records[i]['data'])
                # idMyHyeto = hyetoDict['Ordered To Nb'][idHyeto]
                self.myHyetoDict[idHyeto] = hyetoDict['Hyetos'][idHyeto]
        else:
            print("WARNING: No dbf file")
            time_mod.sleep(5)
            

    def plot(self, workingDir, plotRaw=False, yAdd=[],yAddName=[]):
        ''' This procedure plots:
        - the inlets: in color chosen randomly by matplotlib
        - the outlet: in black solid line 
        - the raw outlet: in black dashed line
        '''

        if(self.model==cst.tom_UH):
            # x = self.time/3600.0
            x = (self.time[:-1]-self.time[0])/3600.0
            
            font11 = FontProperties()
            font11.set_family('serif')
            font11.set_name('Euclid')
            font11.set_size(11)

            font14 = FontProperties()
            font14.set_family('serif')
            font14.set_name('Euclid')
            font14.set_size(14)

            plt.figure(figsize=(11.7,8.3))
            plt.grid()
            plt.xlabel('Temps [h]', fontproperties=font11)
            plt.ylabel('Débits [m³/s]', fontproperties=font11)
            plt.legend(loc="best")
            for i in range(len(self.intletsObj)):
                y = self.intletsObj[i].outFlow
                name = self.intletsObj[i].name
                plt.plot(x, y, label = name)
            if yAdd!=[]:
                # ########
                nbyAdd = np.shape(yAdd)[0]
                for i in range(nbyAdd):
                    y = yAdd[i][:]
                    name = yAddName[i]
                    plt.plot(x, y, label = name)

                # y = yAdd[0][:]
                # name = yAddName[0]
                # plt.plot(x, y, label = name)
                # y = yAdd[1][:]
                # name = yAddName[1]
                # plt.plot(x, y, label = name)
                # y = yAdd[2][:]
                # name = yAddName[2]
                # plt.plot(x, y, label = name)

            # y = self.myHydro
            tmpHydro = np.zeros(len(self.myHydro))
            index = math.floor(self.timeDelay/self.deltaT)
            if(index==0): 
                if(self.model==cst.tom_GR4):
                    tmpHydro = self.myHydro[:,0]
                else:               
                    tmpHydro = self.myHydro
            elif(index<len(self.myHydro)):
                tmpHydro[index:] = self.myHydro[:-index]

            y = tmpHydro
            plt.plot(x, y, label = self.name)
            y = self.myHydro
            plt.plot(x, y,'--',label = self.name+' raw')
            y = self.outFlow
            # plt.plot(x, y, label = 'Outlet '+self.name, color='k')
            plt.plot(x, y, label = 'Outlet', color='k')
            if(plotRaw):
                y = self.outFlowRaw
                plt.plot(x, y, '--', label = 'Outlet '+self.name+' Raw', color='k')
                plt.title(self.name + " Hydrogrammes écrêtés", fontproperties=font14)
            else:
                plt.title(self.name + " Hydrogrammes", fontproperties=font14)
            plt.xlim(x[0], x[-1])
            plt.legend(prop=font11)
            if(plotRaw):
                plt.savefig(workingDir+'PostProcess/QT_HydroEcrete_'+self.name+'.pdf')
            else:
                plt.savefig(workingDir+'PostProcess/QT_Hydro_'+self.name+'.pdf')
            # if(plotRaw):
            #     plt.savefig(workingDir+'QT_HydroEcrete_'+self.name+'.pdf')
            # else:
            #     plt.savefig(workingDir+'QT_Hydro_'+self.name+'.pdf')
        
        elif(self.model==cst.tom_VHM):
            print("ERROR: the plot for VHM is not implemented yet!")
            sys.exit()
        
        else:
            print("ERROR: the plot for this option is not implemented yet!")
            sys.exit()


    def plot_myBasin(self, Measures=None, rangeData=[], yrangeRain=[], yrangeData=[], factor=1.5, graph_title='', withEvap=False, writeFile=''):
        "This procedure plots its own hydrographs and hyetographs"

        # Determine the number of elements according to the model chosen
        if(self.model==cst.tom_UH):
            nbElements = 1
            lastElement = 1
        elif(self.model==cst.tom_VHM):
            nbElements = 4
            lastElement = 0
        elif(self.model==cst.tom_GR4):
            nbElements = 1
            lastElement = 0
        elif(self.model==cst.tom_2layers_linIF):
            nbElements = 3
            lastElement = 0

        # Construction of the list of element to plot on the main hydrograph
        tmpSum = np.zeros(len(self.outFlow)-lastElement)
        y = np.zeros((len(self.outFlow)-lastElement,nbElements))
        if(self.model==cst.tom_UH):
            y[:,0] = self.myHydro[:-1]
        elif(self.model==cst.tom_VHM or self.model==cst.tom_2layers_linIF):
            for i in range(nbElements-1+lastElement):
                y[:,i] = self.myHydro[:,i]
                tmpSum += self.myHydro[:,i]
            y[:,-1] = tmpSum
        elif(self.model==cst.tom_GR4):
            y[:,0] = self.myHydro[:,0]
        else:
            print("ERROR: this model was not implemented yet!")
            sys.exit()
        
        # Add the measures if available
        if(Measures!=None):
            myMeasure = Measures.myHydro

        # label on x-axis
        x_title = "dates"

        # label on y-axis
        y_titles = []
        if(self.model==cst.tom_VHM):   
            y_titles.append("Overland flow")
            y_titles.append("Interflow")
            y_titles.append("Baseflow")
            y_titles.append("Total")
        elif(self.model==cst.tom_UH):
            y_titles.append('')
        elif(self.model==cst.tom_GR4):
            y_titles.append("GR4 flow")
        elif(self.model==cst.tom_2layers_linIF):
            y_titles.append("Overland flow")
            y_titles.append("Interflow")
            y_titles.append("Total")

        if(Measures!=None):
            y_titles.append("Measures")

        # Colors of the plot
        myColors = []
        for i in range(nbElements):
            myColors.append('')
        if(Measures!=None):
            myColors.append('k')

        # Type of trait in the plot
        myTraits = []
        for i in range(nbElements):
            myTraits.append('-')
        if(Measures!=None):
            myTraits.append('--')

        # The additional plots to add
        # Evapotranspiration
        z = []
        y_labelAddPlot = []
        haveUpperPlot = False
        if(withEvap):
            z.append(self.myEvap)
            y_labelAddPlot.append('Evapotranpiration [mm/h]')
            haveUpperPlot = True

        # Graph title:
        if(graph_title==''):
            if(self.name!=None):
                graph_title = "Hydrogramme de " + self.name

        # Range to consider
        if(rangeData==[]):
            rangeData = [self.dateBegin, self.dateEnd]
        if(factor!=1.5 and yrangeRain!=[]):
            print("WARNING: factor and range cannot be specified at the same time. Only factor will be taken into account.")
            yrangeRain=[]
        if(factor!=1.5 and yrangeData!=[]):
            print("WARNING: factor and range cannot be specified at the same time. Only factor will be taken into account.")
            yrangeData=[]


        # Launch the procedure
        if(Measures!=None):
            ph.plot_hydro(nbElements,y,self.myRain,x_title=x_title,y_titles='', beginDate=self.dateBegin,endDate=self.dateEnd,
                        dt=self.deltaT,graph_title=graph_title,y_labels=y_titles,rangeData=rangeData,y_rain_range=yrangeRain,y_data_range=yrangeData,factor_RH=factor,myColors=myColors,typeOfTraits=myTraits,
                        measures=myMeasure,beginDateMeasure=Measures.dateBegin, endDateMeasure=Measures.dateEnd, dtMeasure=Measures.deltaT,
                        upperPlot=haveUpperPlot,nbAddPlot=1,z=z,y_labelAddPlot=y_labelAddPlot,writeFile=writeFile)
        else:
            ph.plot_hydro(nbElements,y,self.myRain,x_title=x_title,y_titles='', beginDate=self.dateBegin,endDate=self.dateEnd,
                        dt=self.deltaT,graph_title=graph_title,y_labels=y_titles,rangeData=rangeData,y_rain_range=yrangeRain,y_data_range=yrangeData,myColors=myColors,typeOfTraits=myTraits,
                        upperPlot=haveUpperPlot,nbAddPlot=1,z=z,y_labelAddPlot=y_labelAddPlot,writeFile=writeFile)

        # x = self.time/3600.0    # [h]
        
        # y1 = self.myHydro
        # y2 = self.rain     

        # # Figure Rain on a first y axis
        # fig,ax1=plt.subplots()
        # ax1.set_xlabel('Temps [h]')
        # ax1.set_ylabel('Débits [m³/s]',color='k') #Color express in %RGB: (1,1,1)
        # ax1.set_ylim(0, self.myHydro.max()*2)
        # # ax1.hist(data1,color=(0,0,1),edgecolor='black',linewidth=1.2)
        # ax1.plot(x,y1, color='k')
        # ax1.tick_params(axis='y',labelcolor='k')

        # # Figure Hydro on a second y axis
        # ax2=ax1.twinx()
        # ax2.set_ylabel('Précipitations [mm/h]',color='b')
        # ax2.set_ylim(self.rain.max()*3, 0)
        # ax2.plot(x,y2,color='b')
        # ax2.fill_between(x, y2, 0, color='b')
        # ax2.tick_params(axis='y',labelcolor='b')
        # fig.tight_layout()


    def plot_outlet(self, Measures=None, rangeData=[], yrangeRain=[], yrangeData=[], ylabel=[],addData=[], dt_addData=[], beginDates_addData=[], endDates_addData=[],\
                    label_addData=[], color_addData=[],factor=1.5, graph_title='', withEvap=False, writeFile='', withDelay=True, deltaMajorTicks=-1,deltaMinorTicks=-1, tzPlot=0):
        "This procedure plots its own hydrographs and hyetographs"

        # Determine the number of elements according to the model chosen
        if(self.model==cst.tom_UH):
            nbElements = 1    ###
            # nbElements = 2  ###
            lastElement = 1
        elif(self.model==cst.tom_VHM):
            nbElements = 4
            lastElement = 0
        elif(self.model==cst.tom_GR4):
            nbElements = 1
            lastElement = 0
        elif(self.model==cst.tom_2layers_linIF):
            nbElements = 3
            lastElement = 0

        # Take into account any additionnal data given and add it to plot
        nbCol_addData = 0
        if(addData!=[]):
            shape_addData = np.shape(addData)
            if(len(shape_addData)==1):
                if(dt_addData==[]):
                    nbCol_addData = 1
                    nbElements += nbCol_addData
                elif(type(addData[0])==list or type(addData[0])==np.ndarray):
                    nbCol_addData = len(addData)
                    nbElements = nbElements + nbCol_addData
                else:
                    nbCol_addData = 1
                    nbElements += nbCol_addData
            elif(len(shape_addData)==2):
                if(type(addData)==list):
                    nbCol_addData = len(addData)
                    nbElements = nbElements + nbCol_addData
                else:
                    nbCol_addData = np.shape(addData)[1]
                    nbElements = nbElements + nbCol_addData
            else:
                print("ERROR : the array additional data (addData) can only be a vector or a matrix!")
                sys.exit()

            # nbElements = nbElements + nbCol_addData
            if(dt_addData!=[]):
                dt = []
                beginDate = []
                endDate = []
                dt.append(self.deltaT)
                beginDate.append(self.dateBegin+datetime.timedelta(hours=tzPlot))
                endDate.append(self.dateEnd+datetime.timedelta(hours=tzPlot))
                for i in range(nbCol_addData):
                    dt.append(dt_addData[i])
                    beginDate.append(beginDates_addData[i]+datetime.timedelta(hours=tzPlot))
                    endDate.append(endDates_addData[i]+datetime.timedelta(hours=tzPlot))
            else:
                dt = self.deltaT
                beginDate = self.dateBegin+datetime.timedelta(hours=tzPlot)
                endDate = self.dateEnd+datetime.timedelta(hours=tzPlot)
        
        else:
            dt = self.deltaT
            beginDate = self.dateBegin+datetime.timedelta(hours=tzPlot)
            endDate = self.dateEnd+datetime.timedelta(hours=tzPlot)


        # Conversion rain from [m³/s] to [mm/h]
        rain = self.rain/self.surfaceDrainedHydro*3.6

        # Construction of the list of element to plot on the main hydrograph
        tmpSum = np.zeros(len(self.outFlow)-lastElement)
        # y = np.zeros((len(self.outFlow)-lastElement,nbElements))
        y = []
        if(self.model==cst.tom_UH or self.model==cst.tom_2layers_linIF):
            if(withDelay):
                # y[:,0] = self.outFlow[:-1]
                y.append(self.outFlow[:-1])
            else:
                tmpSum = self.get_outFlow_noDelay()
                # y[:,0] = tmpSum[:-1]
                y.append(tmpSum[:-1])

            # cumul_rain = datt.cumul_data(self.rain,self.deltaT, self.deltaT)    ###
            # y[:,1] = cumul_rain[:-1]/cumul_rain[-1]*np.max(self.outFlow)    ###

            if nbCol_addData==1:
                # y[:,2] = addData    ###
                # y[:,1] = addData    ###
                # y.append(addData)    ###
                if(type(addData)==list):
                    y.append(addData[0])
                else:
                    y.append(addData[:,0])

            else:
                if(type(addData)==list):
                    for col in range(nbCol_addData):
                        # y[:,1+col] = addData[col]     ###
                        # y[:,2+col] = addData[:,col]     ###
                        y.append(addData[col])     ###
                elif(type(addData)==np.ndarray):
                    for col in range(nbCol_addData):
                        # y[:,1+col] = addData[:,col]     ###
                        # y[:,2+col] = addData[:,col]     ###
                        y.append(addData[:,col])     ###
        


        elif(self.model==cst.tom_VHM):
            print("ERROR : VHM not implemented yet! Please check the code")
            sys.exit()
            for i in range(nbElements-1+lastElement):
                y[:,i] = self.myHydro[:,i]
                tmpSum += self.myHydro[:,i]
            y[:,-1] = tmpSum
        elif(self.model==cst.tom_GR4):
            print("ERROR : GR4 not implemented yet! Please check the code")
            sys.exit()
            y[:,0] = self.outFlow[:,0]
        else:
            print("ERROR: this model was not implemented yet!")
            sys.exit()
        
        # Add the measures if available
        if(Measures!=None):
            myMeasure = Measures.myHydro

        # label on x-axis
        x_title = "Dates"

        # label on y-axis
        y_titles = []
        if(self.model==cst.tom_VHM):   
            y_titles.append("Overland flow")
            y_titles.append("Interflow")
            y_titles.append("Baseflow")
            y_titles.append("Total")
        elif(self.model==cst.tom_UH or self.model==cst.tom_2layers_linIF):
            if(ylabel==[]):
                y_titles.append('Débits simulés')
                # y_titles.append('Avec reconstruction Qout B. Vesdre')
                # y_titles.append('Avec Qout décrit par Le Soir au B. Vesdre')
                # y_titles.append('Débits nuls aux barrages')
                # avec Qout décrit par Le Soir B. Vesdre
                # y_titles.append('Débits décrits dans Le Soir')
                # y_titles.append('Cumulated rain')    ###
            else:
                y_titles.append(ylabel)

            if(label_addData !=[]):
                for ii in label_addData :
                    y_titles.append(ii)
                # y_titles.append(label_addData)

        elif(self.model==cst.tom_GR4):
            y_titles.append("GR4 flow")
        if(Measures!=None):
            # y_titles.append("Measures")
            y_titles.append("Mesures")
            # y_titles.append("Débits entrant reconstruits")

        # Colors of the plot
        myColors = []
        for i in range(nbElements):
            # myColors.append('')
            if(color_addData!=[]):
                if(i>=nbElements-nbCol_addData):
                    myColors.append(color_addData[i+nbCol_addData-nbElements])
                    # myColors.append(color_addData)
                else:
                    myColors.append('')
            else:
                myColors.append('')
        if(Measures!=None):
            myColors.append('k')

        # Type of trait in the plot
        myTraits = []
        for i in range(nbElements):
            myTraits.append('-')
        if(Measures!=None):
            myTraits.append('--')

        # The additional plots to add
        # Evapotranspiration
        z = []
        y_labelAddPlot = []
        haveUpperPlot = False
        if(withEvap):
            z.append(self.myEvap)
            y_labelAddPlot.append('Evapotranpiration [mm/h]')
            haveUpperPlot = True

        # Graph title:
        if(graph_title==''):
            if(self.name!=None):
                graph_title = "Hydrogramme de " + self.name

        # Range to consider
        if(rangeData==[]):
            rangeData = [self.dateBegin, self.dateEnd]
        if(factor!=1.5 and yrangeRain!=[]):
            print("WARNING: factor and range cannot be specified at the same time. Only factor will be taken into account.")
            yrangeRain=[]
        if(factor!=1.5 and yrangeData!=[]):
            print("WARNING: factor and range cannot be specified at the same time. Only factor will be taken into account.")
            yrangeData=[]


        # Launch the procedure
        if(Measures!=None):
            ph.plot_hydro(nbElements,y,rain,x_title=x_title,y_titles='', beginDate=beginDate,endDate=endDate,
                        dt=dt,graph_title=graph_title,y_labels=y_titles,rangeData=rangeData,y_rain_range=yrangeRain,y_data_range=yrangeData,factor_RH=factor,myColors=myColors,typeOfTraits=myTraits,
                        measures=myMeasure,beginDateMeasure=Measures.dateBegin+datetime.timedelta(hours=tzPlot), endDateMeasure=Measures.dateEnd+datetime.timedelta(hours=tzPlot), dtMeasure=Measures.deltaT,
                        upperPlot=haveUpperPlot,nbAddPlot=1,z=z,y_labelAddPlot=y_labelAddPlot,writeFile=writeFile,deltaMajorTicks=deltaMajorTicks,deltaMinorTicks=deltaMinorTicks)
        else:
            ph.plot_hydro(nbElements,y,rain,x_title=x_title,y_titles='', beginDate=beginDate,endDate=endDate,
                        dt=dt,graph_title=graph_title,y_labels=y_titles,rangeData=rangeData,y_rain_range=yrangeRain,y_data_range=yrangeData,myColors=myColors,typeOfTraits=myTraits,
                        upperPlot=haveUpperPlot,nbAddPlot=1,z=z,y_labelAddPlot=y_labelAddPlot,writeFile=writeFile,deltaMajorTicks=deltaMajorTicks,deltaMinorTicks=deltaMinorTicks)


    def create_histo(self, time, hyeto):
        "Transform the hyeto data and its assiciated time in a histogram"
        size = len(hyeto)
        hyeto2 = np.zeros(size*2)
        time2  = np.zeros(size*2)
        for i in range(size):
            time2[i*2+1]  = time[i]
            hyeto2[i*2+1] = hyeto[i]

        time2[0]  = 0
        hyeto2[0] = hyeto2[1]
        for i in range(size-1):
            time2[i*2+2]    = time2[i*2+1]
            hyeto2[i*2+2] = hyeto2[i*2+3]

        plt.figure()
        plt.grid()
        plt.xlabel('temps [h]')
        plt.ylabel('intensité $[mm^3/s]$')
        plt.legend(loc="best")
        plt.title("Hyétogrammes")
        plt.plot(time2, hyeto2)
        plt.plot(time2, hyeto2)
        plt.plot(time2, hyeto2)
        plt.plot(time2, hyeto2)
        plt.xlim(0,time2[len(time2)-1])


    def get_myMainCharacteristics(self, workingDir):
        ''' This procedure read the main characteristics of the subbasin
            TO COMPLETE ...
        '''
        fileName  = "/Subbasin_" + str(self.iDSorted) + "/" + "simul_subbasin.avrg_caractSubBasin"

        with open(workingDir+fileName, newline = '') as fileID2:                                                                                          
            data_reader = csv.reader(fileID2, delimiter='\t')
            list_data = []
            i=0
            for raw in data_reader:
                if i>0:
                    list_data.append(raw)
                i += 1

        tmp = ''
        for i in range(len(list_data)):
            if(list_data[i][0][:4]=="Area"):
                tmp = list_data[i][0].split()
                self.surfaceDrained = float(tmp[1].split("[")[0])
                self.mainCharactDict["Area"] = {}
                self.mainCharactDict["Area"]["value"] = self.surfaceDrained
                self.mainCharactDict["Area"]["unit"] = "["+tmp[1].split("[")[1]
            elif(list_data[i][0][:9]=="Perimeter"):
                tmp = list_data[i][0].split()
                self.mainCharactDict["Perimeter"] = {}
                self.mainCharactDict["Perimeter"]["value"] = float(tmp[1].split("[")[0])
                self.mainCharactDict["Perimeter"]["unit"] = "["+tmp[1].split("[")[1]
            elif(list_data[i][0][:13]=="Average slope"):
                tmp = list_data[i][0].split()
                self.mainCharactDict["Average slope"] = {}
                self.mainCharactDict["Average slope"]["value"] = float(tmp[2].split("[")[0])
                self.mainCharactDict["Average slope"]["unit"] = "["+tmp[2].split("[")[1]
            elif(list_data[i][0][:35]=="Compactness coefficient (Gravelius)"):
                tmp = list_data[i][0].split()
                self.mainCharactDict["Compactness coefficient (Gravelius)"] = {}
                self.mainCharactDict["Compactness coefficient (Gravelius)"]["value"] = float(tmp[3].split("[")[0])
                self.mainCharactDict["Compactness coefficient (Gravelius)"]["unit"] = "[-]"
            elif(list_data[i][0][:12]=="Max lag time"):
                tmp = list_data[i][0].split()
                self.mainCharactDict["Max lag time"] = {}
                self.mainCharactDict["Max lag time"]["value"] = float(tmp[3].split("[")[0])
                self.mainCharactDict["Max lag time"]["unit"] = "["+tmp[3].split("[")[1]
            elif(list_data[i][0][:12] == "Min lag time"):
                tmp = list_data[i][0].split()
                self.timeDelay = float(tmp[3].split("[")[0])
                self.mainCharactDict["Min lag time"] = {}
                self.mainCharactDict["Min lag time"]["value"] = float(tmp[3].split("[")[0])
                self.mainCharactDict["Min lag time"]["unit"] = "["+tmp[3].split("[")[1]
            elif(list_data[i][0][:12]=="Max altitude"):
                tmp = list_data[i][0].split()
                self.mainCharactDict["Max altitude"] = {}
                self.mainCharactDict["Max altitude"]["value"] = float(tmp[2].split("[")[0])
                self.mainCharactDict["Max altitude"]["unit"] = "["+tmp[2].split("[")[1]
            elif(list_data[i][0][:12]=="Min altitude"):
                tmp = list_data[i][0].split()
                self.mainCharactDict["Min altitude"] = {}
                self.mainCharactDict["Min altitude"]["value"] = float(tmp[2].split("[")[0])
                self.mainCharactDict["Min altitude"]["unit"] = "["+tmp[2].split("[")[1]
            elif(list_data[i][0][:21]=="Fraction of landuse n"):
                tmp = list_data[i][0].split()
                self.mainCharactDict["Fraction of landuse n "+tmp[4]] = {}
                self.mainCharactDict["Fraction of landuse n "+tmp[4]]["value"] = float(tmp[5].split("[")[0])
                self.mainCharactDict["Fraction of landuse n "+tmp[4]]["unit"] = "["+tmp[5].split("[")[1]
        

        data_reader = None
        list_data = []
        fileName  = "/Subbasin_" + str(self.iDSorted) + "/" + "simul_subbasin.avrg_caractWholeHydroSubBasin"
        with open(workingDir+fileName, newline = '') as fileID2:                                                                                          
            data_reader = csv.reader(fileID2, delimiter='\t')
            list_data = []
            i=0
            for raw in data_reader:
                if i>0:
                    list_data.append(raw)
                i += 1

        tmp = ''
        for i in range(len(list_data)):
            if(list_data[i][0][:4]=="Area"):
                tmp = list_data[i][0].split()
                self.surfaceDrainedHydro = float(tmp[1].split("[")[0])

    
    def get_flood(self, path='', check_coherence=False):
        
        if(path==''):
            path = self.fileNameRead
        
        paramFile = Wolf_Param(to_read=False)
        paramFile.ReadFile(path +'simul_flood.out.param')
        
        nbFloods = int(paramFile.myparams['Floods characteristics']['nb']['value'])
        dt = float(paramFile.myparams['Floods characteristics']['dt']['value'])

        filePre = "simul_flood"
        floodData = []
        dateMask = []
        mask = np.full((len(self.outFlow)), False, dtype=bool)
        j_saved = 0
        for i in range(nbFloods):
            floodData.append([])
            fileName = filePre + str(i+1) + ".dat"
            floodData[i] = rd.read_bin(path,fileName)
            dateMask.append([])
            # dateMask[i].append(datetime.datetime(year=int(floodData[i][0][2]), month=int(floodData[i][0][1]), day=int(floodData[i][0][0]), hour=int(floodData[i][0][3]), minute=int(floodData[i][0][4]), second=int(floodData[i][0][5]),  microsecond=0, tzinfo=datetime.timezone.utc))
            # dateMask[i].append(datetime.datetime(year=int(floodData[i][-1][2]), month=int(floodData[i][-1][1]), day=int(floodData[i][-1][0]), hour=int(floodData[i][-1][3]), minute=int(floodData[i][-1][4]), second=int(floodData[i][-1][5]),  microsecond=0, tzinfo=datetime.timezone.utc))
            tStart = datetime.datetime.timestamp(datetime.datetime(year=int(floodData[i][0][2]), month=int(floodData[i][0][1]), day=int(floodData[i][0][0]), hour=int(floodData[i][0][3]), minute=int(floodData[i][0][4]), second=int(floodData[i][0][5]),  microsecond=0, tzinfo=datetime.timezone.utc))
            nbElements = len(floodData[i])
            for j in range(j_saved,len(self.outFlow)):
                if(self.time[j]>=tStart):
                    mask[j:j+nbElements] = np.full(nbElements, True, dtype=bool)
                    j_saved = j
                    break
        
        effFlood = np.ma.array(self.outFlow,mask=mask)

        return effFlood

        

    def get_Nash_Flood(self, measures, tMeasures, dateBegin=None, dateEnd=None, path=''):

        if(dateBegin==None):
            dateBegin = self.dateBegin
        if(dateEnd==None):
            dateEnd = self.dateEnd
        if(path==''):
            path = self.fileNameRead
        
        effFlood = self.get_flood(path=path)
        Nash = datt.evaluate_Nash(effFlood.data, self.time, measures, tMeasures, dateBegin, dateEnd, mask=effFlood.mask)

        return Nash

                
        

    # Remove the lines below when it is confirmed
    #                   |
    #                   |
    #                   V
    # ## Function computing the cumulative volume of a given flow
    # # @var flow the flow to treat. Units: [m^3/s]
    # # @var dtData time step of the argument 'flow'. Units: [s]
    # # @var dtOut time step of the desired cumulative volume. It should be a multiple of 'dtData'. Units: [s]
    # # \undeline{Caution}: Take care to the units of dtData and dtOut according to the flow units. 
    # # E.g. Hyeto and Evap in [mm/h]                     => dtData in [h]
    # # \underline{But}: outflow and myHydro in [m^3/s]   => dtData in [sec] 
    # # Returns the cumulative volume. Units: [m^3]
    # # TO do: ajouter interval de temps
    # def construct_cumulVolume(self, flow, dtData, dtOut):
    #     # Check validity of the arguments
    #     if(dtOut%dtData!=0):
    #         print("ERROR: the time step of the desired output is not compatible with the data timestep!")
    #         sys.exit()
    #     else:
    #         factor = int(dtOut/dtData)   # conversion factor from data timestep and cumul time step

    #     cumul = np.zeros(int(len(flow)/factor))
    #     cumul[0] = flow[0]
    #     for i in range(1,int(len(flow)/factor)):
    #         cumul[i] = cumul[i-1] + np.sum(flow[i*factor: (i+1)*factor])*dtData

    #     return cumul
        
