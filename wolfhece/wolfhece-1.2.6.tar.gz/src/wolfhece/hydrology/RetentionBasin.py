import sys
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from scipy.interpolate import interp1d

from .Outlet import *
from .Dumping import *

if not '_' in globals()['__builtins__']: #Test de la présence de la fonction de traduction i18n "gettext" et définition le cas échéant pour ne pas créer d'erreur d'exécution
    import gettext
    _=gettext.gettext

class RetentionBasin():

    def __init__(self, _dateBegin, _dateEnd, _deltaT, _time=[], _id='J1', _name='Default name', _type='', _dictRB={}, _directDictRB={}, _tz=0):
        print('Creation of a RetentionBasin!')
        self.iD = _id
        self.name = _name
        self.type = _type
        self.time = _time
        self.dictRB = {}
        self.alreadyUsed = False
        self.isLeveled = False
        self.myLevel = 2
        self.dateBegin = _dateBegin
        self.dateEnd = _dateEnd
        self.deltaT = _deltaT
        self.tz = _tz
        if(_time==[]):
            print("TO DO!!!!")
            sys.exit()



        # Dimensions
        self.hFloor = 0.0
        self.hBank = 0.0
        self.hStagn = 0.0
        self.volume = 0.0
        self.surface = 0.0
        self.hi = 0.0

        # inlets and outlets
        self.intletsObj = []
        self.inlets = []
        self.inletsRaw = []

        self.directFluxObj = []
        self.directFluxInRB = []
        self.directFluxInRB_Raw = []
        self.downstreamObj = None
        self.outFlow = []
        self.outFlowRaw = []

        self.rain = []
        
        self.filledVolume = []
        self.qLim = None        # object to compute "l'ecretage"

        self.outletObj = None   # object to compute the outlet 

        self.zData = []         # height from z-v file stored 
        self.vData = []         # volume from z-v file stored
        self.zvInterpol = None

        self.timeDelay = 0.0    # [s]????? -> A vérifier!!!


        if(_dictRB!={}):
            # Init of the object allowing to determine the outlet flux
            tmpCounter = 0
            for element in _dictRB:
                if(_dictRB[element]['from']['value'] == self.iD):
                    if(tmpCounter>0):
                        print("ERROR: the same RB associated to two different caracteristics. Please check the RetentionBasin.postPro file.")
                        sys.exit()
                    self.dictRB = _dictRB[element]
                    tmpCounter +=1
            if(tmpCounter == 0):
                print("Error: no RB associated! Please check the RetentionBasin.postPro file.")
                sys.exit()
        elif(_directDictRB!={}):
            self.dictRB = _directDictRB
        else:
            print("ERROR: Not enough elements, it lacks a least a dictionary!")
            sys.exit()


        self.type = self.dictRB['type']['value']
        if('stagnant height' in self.dictRB):
            self.hStagn =  float(self.dictRB['stagnant height']['value'])
        if(self.type == 'HighwayRB'):
            self.surface = float(self.dictRB['surface']['value'])
            self.hBank = float(self.dictRB['height 2']['value'])
            self.volume = self.surface * self.hBank
        elif(self.type == 'RobiernuRB'):
            self.volume = float(self.dictRB['volume']['value'])
        elif(self.type == 'OrbaisRB'):
            self.volume = float(self.dictRB['volume']['value'])
            try:
                zvFile = self.dictRB['Z-V file']['value']
            except:
                zvFile = ""
            if(zvFile!=""):
                zvFile = zvFile.replace("\\", "/")
                self.read_zv(zvFile)
                
            # self.qLim = float(self.dictRB['ecretage']['value'])
        elif(self.type == 'HelleRB'):
            self.volume = float(self.dictRB['volume']['value'])
            print("ERROR: Not implemented yet!")
            sys.exit()
        elif(self.type == 'ForcedDam'):
            self.volume = float(self.dictRB['volume']['value'])
            self.hi = float(self.dictRB['initial height']['value'])
            try:
                zvFile = self.dictRB['Z-V file']['value']
            except:
                zvFile = ""
            if(zvFile!=""):
                zvFile = zvFile.replace("\\", "/")
                self.read_zv(zvFile)
            if("time delay" in self.dictRB):
                self.timeDelay = float(self.dictRB["time delay"]["value"])

        else:
            print("WARNING: This type RB was not recognised! Please check the RetentionBasin.postPro file.")


        if ("initial height" in self.dictRB):
            self.hi = float(self.dictRB['initial height']['value'])
        
        if("time delay" in self.dictRB):
            self.timeDelay = float(self.dictRB["time delay"]["value"])

         # Creation of Outlet object
        self.outletObj = Outlet(self.dictRB)
        self.qLim = Dumping(self.dictRB)
        
        
        
        # if('direct inside RB' in self.myCatchment[self.iD]):
        #     if(self.myCatchment[self.iD]['direct inside RB'] != ''):
        #         self.sum_directFluxInRB()
        # self.sumHydro = self.run()
        # print(self.sumHydro)<


    def increment_level(self):
        "This procedure increment the level in the Topo dictionary"
        self.myLevel += 1


    def add_inlet(self, toPoint):
        "This procedure link the inlets to the object"
        self.intletsObj.append(toPoint)


    def add_downstreamObj(self, toPoint):
        "This procedure link the downstream element to the object"
        self.downstreamObj = toPoint


    def add_directFluxObj(self, toPoint):
        "This procedure link the direct inlet elements to the object"
        self.directFluxObj.append(toPoint)


    def compute_hydro(self, givenDirectFluxIn=[], givenInlet=[]):
        """ This function computes the raw and real hydrographs.
            
            The volume filled and then the water height in the RB at time $t$ will be evaluated will depend of the flows
            at time $t-1$ exept if the 

            Internal variables modified : self.inlets, self.inletsRaw, 
                                        self.directFluxInRB, self.directFluxInRB_Raw,
                                        self.outFlowRaw, self.outFlow, self.filledVolume
        """
        self.sum_inlets(givenInlet)
        self.sum_directFluxInRB(givenDirectFluxIn)
        self.outFlowRaw = self.inletsRaw + self.directFluxInRB_Raw


        sizeOfHydro = len(self.time)-1
        # Volume of the RB filled with water
        self.filledVolume = np.zeros(sizeOfHydro)
        self.outFlow =  np.zeros(sizeOfHydro)
        
        self.filledVolume[0] = self.h_to_volume(self.hi)
        for i in range(1,sizeOfHydro):
            # # To avoid a division by zero and physically correct.
            # if(self.surface == 0.0):
            #     h = 0.0
            # else:
            #     h = self.filledVolume[i-1]/self.surface
            # 1st evaluation of the outlet of the RB according to Vfilled at the previous time
            h = self.volume_to_h(self.filledVolume[i-1])
            # Qout = self.outletObj.compute(h,self.time[self.convert_index_global_to_local(i)])
            Qout = self.outletObj.compute(h,self.convert_time_global_to_local(self.time[i]))
            qLim = self.qLim.compute(h,self.convert_time_global_to_local(self.time[i]))
            diff = self.directFluxInRB[i-1]+max(self.inlets[i-1]-qLim,0.)-Qout
            self.outFlow[i-1]=Qout
            # If the volume increase => the outflow is kept (Maybe to improve!! The height can go to the upper threshold)
            if diff>0:
                self.filledVolume[i] = self.filledVolume[i-1] + diff*(self.time[i]-self.time[i-1])
            # If the volume is decreasing but is not enough to empty it at this time step
            elif self.filledVolume[i-1]>abs(diff*(self.time[i]-self.time[i-1])):
                self.filledVolume[i] = self.filledVolume[i-1] + diff*(self.time[i]-self.time[i-1])
                # if(self.surface == 0.0):
                #     h = 0.0
                # else:
                #     h = self.filledVolume[i]/self.surface
                h = self.volume_to_h(self.filledVolume[i])
                # All the values:
                    # -outlet, 
                    # -ecretage,
                    # -volume,
                # will be reevaluated. Because we can go to the lower threshold.
                # Qout = self.outletObj.compute(h,self.time[self.convert_index_global_to_local(i)])
                Qout = self.outletObj.compute(h,self.convert_time_global_to_local(self.time[i]))
                qLim = self.qLim.compute(h,self.convert_time_global_to_local(self.time[i]))
                diff = self.directFluxInRB[i-1]+max(self.inlets[i-1]-qLim,0.)-Qout
                self.outFlow[i-1] = Qout
                self.filledVolume[i] = self.filledVolume[i-1] + diff*(self.time[i]-self.time[i-1])


            else:
                self.filledVolume[i] =0
                self.outFlow[i-1] = self.filledVolume[i-1]/((self.time[i]-self.time[i-1]))+self.directFluxInRB[i-1]+max(self.inlets[i-1]-qLim,0.)

            if self.filledVolume[i]>self.volume:
                self.outFlow[i-1] += (self.filledVolume[i]-self.volume)/((self.time[i]-self.time[i-1]))
                self.filledVolume[i] = self.volume

            self.outFlow[i-1]+=min(self.inlets[i-1],qLim)

        return self.outFlow
            

    def sum_inlets(self, givenInlet=[]):
        """ This procedure sum all the inlets of the RB
            Caution: inlets variable is different from directFluxIn !!

            Internal variables modified: self.inlets, self.inletsRaw
        """
        if(self.intletsObj != []):
            self.inlets = self.intletsObj[0].outFlow.copy()
            self.inletsRaw = self.intletsObj[0].outFlowRaw.copy()
            for i in range(1,len(self.intletsObj)):
                self.inlets += self.intletsObj[i].outFlow
                self.inletsRaw += self.intletsObj[i].outFlowRaw
        elif(givenInlet != []):
            if(len(givenInlet)!=len(self.time)-1):
                print("ERROR: the dimension of the time array and the given inlet are not the same!")
                sys.exit()
            self.inlets = givenInlet
            self.inletsRaw = givenInlet
        else:
            self.inlets = np.zeros(len(self.time)-1)        # the size of outflow will always be 1 element smaller than time (convention)
            self.inletsRaw = np.zeros(len(self.time)-1)     # the size of outflow will always be 1 element smaller than time (convention)


    def sum_directFluxInRB(self, givenDirectFluxIn=[]):
        """This procedure computes the flux going directly inside the RB

            Internal variables modified: self.directFluxInRB, self.directFluxInRB_Raw
        """
        if(self.directFluxObj != []):
            self.directFluxInRB = self.directFluxObj[0].outFlow.copy()
            self.directFluxInRB_Raw = self.directFluxObj[0].outFlowRaw.copy()
            for i in range(1,len(self.directFluxObj)):
                self.directFluxInRB += self.directFluxObj[i].outFlow
                self.directFluxInRB_Raw += self.directFluxObj[i].outFlowRaw
        elif(givenDirectFluxIn != []):
            if(len(givenDirectFluxIn)!=len(self.time)-1):
                print("ERROR: the dimension of the time array and the given inlet are not the same!")
                sys.exit()
            self.directFluxInRB = givenDirectFluxIn
            self.directFluxInRB_Raw = givenDirectFluxIn
        else:
            self.directFluxInRB = np.zeros(len(self.time)-1)
            self.directFluxInRB_Raw = np.zeros(len(self.time)-1)


    def plot(self, workingDir, plotRaw=True):
        ''' This procedure plots:
        - the inlets: in color chosen randomly by matplotlib
        - DirectIn : in color chosen randomly by matplotlib and in '-.' lines
        - the outlet: in black solid line 
        - the raw outlet: in black dashed line
        '''

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

        plt.figure(figsize=(8.3, 11.7))
        plt.subplot(2,1,1)

        plt.subplot(2,1,1)
        plt.grid()
        plt.xlabel('Temps [h]', fontproperties=font11)
        plt.ylabel('Débits [m³/s]', fontproperties=font11)
        plt.legend(loc="best")
        plt.title(self.name + " Hydrogrammes écrêtés", fontproperties=font14)
        for i in range(len(self.intletsObj)):
            y = self.intletsObj[i].outFlow
            name = self.intletsObj[i].name
            plt.plot(x, y, label = name)
        for i in range(len(self.directFluxObj)):
            y = self.directFluxObj[i].outFlow
            name = self.directFluxObj[i].name
            if(name=="ss 18" or name=="ss 19"):
                name = "Qin BV"
            plt.plot(x, y, '-.', label = name)
        y = self.outFlow
        plt.plot(x, y, label = self.name, color='k')
        y = self.outFlowRaw
        plt.plot(x, y, '--', label = self.name+' Raw', color='k')
        plt.xlim(x[0], x[len(x)-1])
        plt.legend(prop=font11)
        try:
            plt.savefig(workingDir+'PostProcess/QT_HydroEcrete_'+self.name+'.pdf')
        except:
            plt.savefig(workingDir+'/QT_HydroEcrete_'+self.name+'.pdf')

        plt.subplot(2,1,2)
        plt.grid()
        plt.xlabel('Temps [h]', fontproperties=font11)
        plt.ylabel('Volume [m³]', fontproperties=font11)
        plt.legend(loc="best", prop=font11)
        plt.title("Volume cumulé", fontproperties=font11)
        y = self.filledVolume
        plt.plot(x, y, label = self.name)
        y = self.volume*np.ones(len(x))
        plt.plot(x, y, '--', label = "Volume max")
        plt.xlim(x[0], x[len(x)-1])
        plt.legend(prop=font11)
        plt.savefig(workingDir+'PostProcess'+self.name+'.pdf')


    def add_rain(self, workingDir, tzDelta=datetime.timedelta(hours=0)):
        """ This function returns the a time array and a array containing the sum of all the rain in the inlets
            Value changed :  self.rain
        """
        if(self.directFluxObj == []):
            rain = np.zeros(len(self.intletsObj[0].rain))
        else:
            rain = np.zeros(len(self.directFluxObj[0].rain))
        for i in range(len(self.intletsObj)):
            rain += self.intletsObj[i].rain
        for i in range(len(self.directFluxObj)):
            rain += self.directFluxObj[i].rain
        self.rain = rain
        return self.time

    
    def volume_to_h(self, volume):

        if(volume==0.0):
            h=0
        elif(self.zData!=[]):
            if(volume>max(self.zvVtoHInterpol.x)):
                # h = max(self.zvVtoHInterpol.y)
                slope = (self.zvVtoHInterpol.y[-1]-self.zvVtoHInterpol.y[-2])/(self.zvVtoHInterpol.x[-1]-self.zvVtoHInterpol.x[-2])
                h = slope*(volume-self.zvVtoHInterpol.x[-1])+max(self.zvVtoHInterpol.y)
            else:
                h = self.zvVtoHInterpol(volume)
        else:
            if(self.surface == 0.0):
                h = 0.0
            else:
                h = volume/self.surface
        
        return h


    def h_to_volume(self, h):

        if(h==0):
            vol = 0
        elif(self.zData!=[]):
            if(h>max(self.zvHtoVInterpol.x)):
                h_tmp=max(self.zvHtoVInterpol.y)
                vol = self.zvHtoVInterpol(h_tmp)
            else:
                vol = self.zvHtoVInterpol(h)
        else:
            vol = h*self.surface
        
        return vol
    

    def read_zv(self, fileName, typeOfInterpolation='linear'):

        with open(fileName, newline = '') as fileID:                                                                                          
            data_reader = csv.reader(fileID, delimiter='\t')
            list_data = list(data_reader)
        matrixData = np.array(list_data).astype("float")
        self.zData = matrixData[:,0]
        self.vData = matrixData[:,1]

        self.zvVtoHInterpol = interp1d(self.vData,self.zData,kind=typeOfInterpolation)  # kind is 'linear' by default in interp1d
        self.zvHtoVInterpol = interp1d(self.zData,self.vData,kind=typeOfInterpolation)

    
    def convert_index_global_to_local(self, i):

        index = math.floor(self.timeDelay/(self.time[1]-self.time[0]))
        index = i - index

        if(index<0):
            index = 0

        return index


    def convert_time_global_to_local(self, time):

        realTime = time - self.timeDelay

        return realTime


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

    
    def write_height_reservoir(self, workingDir):

        myH = np.zeros(len(self.filledVolume))
        for ii in range(len(self.filledVolume)):
            myH[ii] =  self.volume_to_h(self.filledVolume[ii])
    
        DataWrite = []
        for ii in range(len(self.filledVolume)):
            dateData = datetime.datetime.fromtimestamp(self.time[ii]-self.timeDelay,tz=datetime.timezone.utc)
            strDated = dateData.strftime("%d/%m/%Y %H:%M:%S")
            DataWrite.append([strDated, myH[ii]])
        
        f = open(workingDir+self.name+'_H.csv', 'w')
        writer = csv.writer(f, delimiter="\t")
        for row in DataWrite:
            writer.writerow(row)