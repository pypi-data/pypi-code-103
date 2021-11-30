from operator import index
import numpy  as np
from numpy.core.numeric import False_
import numpy.ma as ma
import csv
import time as time_mod
import sys                              # module to stop the program when an error is encountered
import json                             # mudule to use json file
import pandas as pd                     # module to write data in Excel file
import datetime                         # module which contains objects treating dates
import matplotlib.pyplot as plt
from dbfread import DBF                 # module to treat DBF files

if not '_' in globals()['__builtins__']: #Test de la présence de la fonction de traduction i18n "gettext" et définition le cas échéant pour ne pas créer d'erreur d'exécution
    import gettext
    _=gettext.gettext

#  libraries to import for graphiz (Here to draw flowcharts)
import graphviz
import os
import copy                             # module to copy objects
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz/bin'    # Without this line the path to graphiz app might not be found
# Note: do not forget to install the graphviz app and add it to the PATH to make it work
# -------------------------------- 

from .SubBasin import *
from .RetentionBasin import *
from ..wolf_array import *
from ..PyParams import*

class Catchment:
    """This object contains all the information about the Catchment.

        The Catchment is composed of element that can be:
            - Subbasin
            - RetentionBasin
        
        In the Catchment the following rules are applied:
            - there is one and only one outlet.
            - one element 
            
    """



    def __init__(self, _name, _workingDir, _plotAllSub, _plotNothing, _initWithResults=True, _catchmentFileName="", _rbFileName="", _tz=0):
        "This is the constructor of the class Catchment in which all the caractertics and the network of sub-basins will be created"
        # Init of all the propperties' object
        self.name = _name
        self.workingDir = _workingDir
        self.plotAllSub = _plotAllSub
        self.plotNothing = _plotNothing
        if(self.plotNothing == True):
            self.plotAllSub = False
        self.tz = _tz                                                       # time zone in GMT+0
        self.time = []                                                      #
        self.deltaT = 0.0                                                   # Time step of the simulation
        self.dateBegin = None                                               # Object datetime of the beginning date of the simulation
        self.dateEnd = None                                                 # Object datetime of the end date of the simulation
        self.myModel = None
        self.nbCommune = 0
        self.nbSubBasin = 0
        self.hyeto = {}                                                     # Pluie pour chaque "commune"
        self.catchmentDict = {}
        self.subBasinDict = {}
        self.retentionBasinDict = {}
        self.topologyDict = {}
        self.dictIdConversion = {}
        self.hyetoDict = {}
        self.intersection = {}
        self.catchmentDict['Elements'] = {}
        self.catchmentDict['Subbasin'] = self.subBasinDict
        self.catchmentDict['RB'] = self.retentionBasinDict
        self.catchmentDict['Topo'] = self.topologyDict
        self.catchmentDict['Hyeto'] = self.hyeto
        self.catchmentDict['dictIdConversion'] = self.dictIdConversion

        if(_initWithResults==False):
            return

        # Creation of the PostProcess directory
        # It will contain all the the saved results.
        writingDir = self.workingDir + 'PostProcess/'
        if not os.path.exists(writingDir):
            try:
                os.mkdir(writingDir)
            except OSError:
                print ("Creation of the directory %s failed" % writingDir)
            else:
                print ("Successfully created the directory %s" % writingDir)
        
        # Read the input files
        # read the Main File
        self.paramsInput = Wolf_Param(to_read=False)
        self.paramsInput.ReadFile(self.workingDir +'Main_model.param')
        # read the topology file
        self.paramsTopology = Wolf_Param(to_read=False)
        if(self.paramsInput is self.paramsTopology):
            print("Error: the same Wof_Param object was created")
            sys.exit()
        
        if(_catchmentFileName==""):
            catchmentFileName = 'Catchment.postPro'
        else:
            catchmentFileName = _catchmentFileName           
        self.paramsTopology.ReadFile(self.workingDir + catchmentFileName)
        if(self.paramsInput.myparams is self.paramsTopology.myparams):
            print("Error: the same dictionnary was created for the params in the input files")
            sys.exit()
        # Read data and characteristics of the RB and its outlet
        self.paramsRB = Wolf_Param(to_read=False)
        if(self.paramsRB is self.paramsTopology):
            print("Error: the same Wof_Param object was created")
            sys.exit()
        
        if(_rbFileName==""):
            rbFileName = 'RetentionBasins.postPro'
        else:
            rbFileName = _rbFileName
        self.paramsRB.ReadFile(self.workingDir + rbFileName)
        if(self.paramsRB.myparams is self.paramsTopology.myparams):
            print("Error: the same dictionnary was created for the params in the input files")
            sys.exit()

        # Get the number of subbasins
        try:
            self.nbSubBasin = int(self.paramsInput.myparams['Semi distributed model']['How many?']['value']) + 1 # +1 because the outlet is also counted
        except:
            self.nbSubBasin = int(self.paramsInput.myparams_default['Semi distributed model']['How many?']['value']) + 1 # +1 because the outlet is also counted

        # Fill the dictionary containing the id of the sorted subbasin returned by the Fortran code
        self.init_dictIdConversion(self.workingDir)

        # Fill the dictionary containing the id of the hyeto to read when the ordred hyeto is given
        self.init_hyetoDict()

        # Get the information on the characteristic maps computed by the Fortran code 
        # self.topo_wolf_array = WolfArray(self.workingDir + "Characteristic_maps/Drainage_basin.b")
        # self.topo_wolf_array = WolfArray(self.workingDir + "Characteristic_maps/Drainage_basin.b2")
        self.time_wolf_array = WolfArray(self.workingDir + "Characteristic_maps/Drainage_basin.time")
        self.conv_wolf_array = WolfArray(self.workingDir + "Characteristic_maps/Drainage_basin.cnv")

        # time array:
        self.get_time()
        # self.time, self.rain = self.get_rain(self.workingDir+'Subbasin_1/')
        # TO DO: Check how the rain is read for the first time

        # Get the hydrology model used (1-linear reservoir, 2-VHM, 3-Unit Hydrograph)
        self.myModel = int(self.paramsInput.myparams['Model Type']['Type of hydrological model']['value'])





        
        # Construction of the Catchment 
        # ------------------------------

        # 1) 1st Iteration: Object creation
        
        # Iterate through the Input params dictionnary
        self.create_ObjectsInCatchment()
            
        # self.add_hyetoToDict()


        # 2) 2nd Iteration: Link between objects
        self.link_objects()   # This procedure also creates the first layer of the topo tree by identifying the source ss-basins

        '''
        The topo tree is organised by level:
        - The first level contains should only contain subbasins which don't have any input flows. 
          Therefore, they already contains all the information to build their hydrograph
        - The second and upper levels can contain either RB or subbasins with input flows.

        '''

        # 3) 3rd Iteration: Complete the tree
        self.complete_topoDict()
        if(not(self.plotNothing)):
            flowchart = graphviz.Digraph("Test")
            self.draw_flowChart(flowchart)
            flowchart.view()
            flowchart.save(directory=self.workingDir)
            isNotCorrect = True
            while(isNotCorrect):
                print("Is this Flowchart ok?")
                print("Y-Yes, N-No")
                answer = input("Your answer:")
                if(answer=="N" or answer=="No"):
                    print("The postprocess was stopped by the user!")
                    sys.exit()
                elif(answer=="Y" or answer=="Yes"):
                    isNotCorrect = False
                else:
                    print("ERROR: Please enter the correct answer!")

        # ===============================
        # Computation of the hydrographs
        self.construct_hydro()

        # Reading of the rain for each subbasin

        self.add_rainToAllObjects()

        # ==============================
        # Save in excel file all the hydrographs 

        # Hello! To uncomment!!!!
        # self.save_ExcelFile()
        # self.save_ExcelFile_noLagTime()
        # self.save_ExcelFile_V2()
        # self.save_characteristics()

        # Plot the of the subbasin or RB with level above 1 in the topo tree
        if(not(self.plotNothing)):
            self.plot_intersection()
        # Plot all the subbasin hydrographs and hyetograph
        if(self.plotAllSub):
            self.plot_allSub()
        




    def get_time(self):
        ''' This method saves the time characteristics read in the .param file and build a time array.
            The convention used for the time written in the .param is as follow: YYYYMMDD-HHMMSS
            It is important to notice that the dateBegin and dateEnd are converted in GMT+0

            Internal variables modified : self.deltaT, self.dateBegin, self.dateEnd, self.time.

            NB : If any change in the convention is mentionned in the comment following the dates the code will return an error
                Otherwise, no procedure will warn the user that a converntion is modified.
        '''
        commentRead1 = self.paramsInput.myparams_default['Temporal Parameters']['Start date time']['comment']
        commentRead2 = self.paramsInput.myparams_default['Temporal Parameters']['End date time']['comment']
        if (commentRead1.replace(' ', '') != 'Startdate[YYYYMMDD-HHMMSS]'):
            print("ERROR: The convention in the start date is different from the one treated in this code. Please change it or modify the function get_time().")
            sys.exit()
        if (commentRead2.replace(' ', '') != 'Enddate[YYYYMMDD-HHMMSS]'):
            print("ERROR:The convention in the end date is different from the one treated in this code. Please change it or modify the function get_time().")
            sys.out()
        try:
            dateRead1 = self.paramsInput.myparams['Temporal Parameters']['Start date time']['value']
        except:
            dateRead1 = self.paramsInput.myparams_default['Temporal Parameters']['Start date time']['value']
        
        try:
            dateRead2 = self.paramsInput.myparams['Temporal Parameters']['End date time']['value']
        except:
            dateRead2 = self.paramsInput.myparams_default['Temporal Parameters']['End date time']['value']
        tzDelta = datetime.timedelta(hours=self.tz)
        self.deltaT = float(self.paramsInput.myparams['Temporal Parameters']['Time step']['value'])
        self.dateBegin = datetime.datetime(year=int(dateRead1[0:4]), month=int(dateRead1[4:6]), day=int(dateRead1[6:8]), hour=int(dateRead1[9:11]), minute=int(dateRead1[11:13]), second=int(dateRead1[13:15]),  microsecond=0, tzinfo=datetime.timezone.utc)
        self.dateBegin -= tzDelta
        self.dateEnd = datetime.datetime(year=int(dateRead2[0:4]), month=int(dateRead2[4:6]), day=int(dateRead2[6:8]), hour=int(dateRead2[9:11]), minute=int(dateRead2[11:13]), second=int(dateRead2[13:15]),  microsecond=0, tzinfo=datetime.timezone.utc)
        self.dateEnd -= tzDelta
        diffDate = self.dateEnd - self.dateBegin
        # secondsInDay = 24*60*60
        # diffTimeInSeconds = diffDate.days*secondsInDay + diffDate.seconds
        ti = datetime.datetime.timestamp(self.dateBegin)
        tf = datetime.datetime.timestamp(self.dateEnd)
        # self.time = np.arange(0,diffTimeInSeconds+1,self.deltaT)
        self.time = np.arange(ti,tf+self.deltaT,self.deltaT)

    

    def get_rain(self, workingDir):
        fileName = 'simul_lumped_rain.txt'
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
        for i in range(len(matrixData)):
            time[i] = matrixData[i][4]*60 + matrixData[i][3]*60**2 + (matrixData[i][0]-matrixData[0][0])*(60**2)*24 + (matrixData[i][1]-matrixData[0][1])*(60**2)*24*31
            rain[i] = matrixData[i][6]

        return time, rain



    def get_hyeto(self, fileName):
        f = open(fileName, "r")
        stringTab = []
        for line in f:
            stringTab.append(line.lstrip())

        matrixData = np.zeros((len(stringTab)-1,2))
        for i in range(len(stringTab)):
            if(i>0):
                tmpTxt = stringTab[i].split(" ", 1)
                tmpTxt[1] = tmpTxt[1].strip()
                tmpTxt[1] = tmpTxt[1].replace("\n", "")
                matrixData[i-1][0] = float(tmpTxt[0])
                matrixData[i-1][1] = float(tmpTxt[1])

        rain = np.zeros(len(matrixData))
        time = np.zeros(len(matrixData))
        time0 = matrixData[0][0]
        for i in range(len(matrixData)):
            time[i] = matrixData[i][0]-time0
            rain[i] = matrixData[i][1]
        return time, rain



    def init_dictIdConversion(self, workingDir):
        ''' Procedure that converts the Id of the intersection points in the input file into the sorted sub-basin ids
            file read: simul_sorted_interior_points.txt
            Internal variables modified: self.dictIdConversion

            The conversion dictionnary has the given form:
            self.dictIdConversion[Internal Point id] = sorted subbasin from the lowest to the highest
        '''      
        fileNameInteriorPoints = workingDir + 'simul_sorted_interior_points.txt'

        # !!! Add the case the file is not present.
        with open(fileNameInteriorPoints) as fileID:                                                                                     
            data_reader = csv.reader(fileID, delimiter='\t')
            list_data = []
            i=0
            for raw in data_reader:
                if i>0:
                    list_data.append([int(raw[i].replace(' ','')) for i in range(0,len(raw))])
                i += 1 

        nbData = len(list_data)
        if(self.nbSubBasin != nbData):
            if(self.nbSubBasin == 0):
                print("WARNING : The number of subbasins not encoded yet")
            else:
                print("ERROR : The number subbasin is not consistent with the number of lines in the file: simul_sorted_interior_points.txt")
                sys.exit()

        for num in range(1, nbData+1):
            for index in range(nbData):
                if (list_data[index][0]==num):
                    self.dictIdConversion[num] = list_data[index][1]
                    break
                if(index == nbData-1):
                    print("Not normal:" , num)



    def create_ObjectsInCatchment(self):
        ''' Procedure which creates the objects in the dictionnaries of the subbasins and the RB and
            each object are pointed in the global catchment dictionnary.
            This procedre also create the 1st level of the Topo dictionnary.
            Internal variables modified: subBasinDict, retentionBasinDict, self.catchmentDict, 
        '''
        # Creates Subbasins
        counter = 0
        for counter in range(1, self.nbSubBasin):
            tmpNameParam = 'Interior point '+ str(counter)
            x = float(self.paramsInput.myparams[tmpNameParam]['X']['value'])    
            y = float(self.paramsInput.myparams[tmpNameParam]['Y']['value'])
            idSorted = self.catchmentDict['dictIdConversion'][counter]
            # self.subBasinDict[counter] = SubBasin(counter, self.time, self.workingDir, self.hyeto, x, y, idSorted)
            self.subBasinDict[counter] = SubBasin(self.dateBegin, self.dateEnd, self.deltaT, self.myModel, self.workingDir,
                                         _iD_interiorPoint=counter, _idSorted=idSorted, _hyeto=self.hyeto, _x=x, _y=y, _tz=self.tz)
            self.catchmentDict['ss'+str(counter)] = self.subBasinDict[counter]
        counter += 1
        tmpNameParam = 'Outlet Coordinates'
        x = float(self.paramsInput.myparams[tmpNameParam]['X']['value'])
        y = float(self.paramsInput.myparams[tmpNameParam]['Y']['value'])
        idSorted = self.catchmentDict['dictIdConversion'][counter]
        # self.subBasinDict[counter] = SubBasin(counter, self.time, self.workingDir, self.hyeto, x, y, idSorted)
        self.subBasinDict[counter] = SubBasin(self.dateBegin, self.dateEnd, self.deltaT, self.myModel, self.workingDir,
                                     _iD_interiorPoint=counter, _idSorted=idSorted, _hyeto=self.hyeto, _x=x, _y=y, _tz=self.tz)
        self.catchmentDict['ss'+str(counter)] = self.subBasinDict[counter]

        # Creates RB and checking if the topo file contains only these types of junction
        for element in self.paramsTopology.myparams:
            # If Subbasin:
            if(self.paramsTopology.myparams[element]['type']['value'] == 'Subbasin'):
                idBasin = int(self.paramsTopology.myparams[element]['number']['value'].replace('ss', ''))
                nameBasin = self.paramsTopology.myparams[element]['name']['value']
                inletsString = self.paramsTopology.myparams[element]['inlets']['value'].strip()
                # Save the name of the basin
                self.subBasinDict[idBasin].add_name(nameBasin)
                # Check if the subbasin have inlets or not => if not can be on the first layer of the topology tree.
                if(inletsString!='--'):
                    self.subBasinDict[idBasin].change_haveInlets()
                # Save the element of the subbasin dictionnary also in the global Cachment dictionnary with 'J' prefix.
                self.catchmentDict[element] = self.subBasinDict[idBasin]
                # Save the element of the subbasin dictionnary also in the global Cachment dictionnary with 'ss' prefix
                # -> First free the object aleady created with the 'ss' prefix 
                # Therefore a subbasin with several inputs can be called in the Catchment dictionnary with 'J' and 'ss' name 
                self.catchmentDict[self.paramsTopology.myparams[element]['number']['value']] = None
                self.catchmentDict[self.paramsTopology.myparams[element]['number']['value']] = self.subBasinDict[idBasin]
            # If RB:
            elif(self.paramsTopology.myparams[element]['type']['value'] == 'RB'):
                idBasin = element
                # Save the name of the RB
                nameBasin = self.paramsTopology.myparams[element]['name']['value']
                # Create the RB object
                typeOfRB = self.paramsTopology.myparams[element]['type of RB']['value']
                self.retentionBasinDict[element] = RetentionBasin(self.dateBegin, self.dateEnd, self.deltaT, self.time, idBasin, nameBasin, typeOfRB, self.paramsRB.myparams, _tz=self.tz)
                # Save the RB in the RB dictionnary into the global Catchment dictionnary
                self.catchmentDict[element] = self.retentionBasinDict[element]
            # If none of the junction above
            else:
                print("ERROR: This type of junction is unknown. Please check the topo postprocess file")
                sys.exit()



    def link_objects(self):
        ''' This procedure link all the subbasins and the retention basin altogether to form a network.
            If a subbasin without inlet whatsoever is detected, one adds it to the first level of the Topology tree.

            Internal variables modified: subBasinDict, retentionBasinDict, topologyDict

        '''
        print("Procedure of objects linking ongoing")
        nbSub = 0
        nbInter = 0
        self.topologyDict['Level 1'] = {}
       
        if len(self.paramsTopology.myparams)==0 :
            self.topologyDict['Level 1']['ss1'] = self.subBasinDict[1]

        for element in self.paramsTopology.myparams:
            if(self.paramsTopology.myparams[element]['type']['value'] == 'RB'):
                # Case 1) inlets
                if('inlets' in self.paramsTopology.myparams[element]):
                    # Split the string at each ',' in several smaller strings
                    tmpString = self.paramsTopology.myparams[element]['inlets']['value'].split(',')
                    # Loop on the strings representing the inlets
                    for i in range(len(tmpString)):
                        # Remove leading and trailing white spaces
                        tmpString[i]= tmpString[i].strip()
                        # If the inlet is a subbasin
                        if tmpString[i][0:2] == 'ss' :
                            # This variable will count the number of subbasins to check if all of them are used.
                            nbSub += 1
                            # In the subbasin dict, only the number is kept as identifier.
                            iDSub =  int(tmpString[i].replace('ss', ''))
                            # Check if the subbasin were already used or not. It cannot be used more than once.
                            if(self.subBasinDict[iDSub].alreadyUsed):
                                print("ERROR: a subbasin has already been used. Please check the topology file!")
                                sys.exit()
                            # The RB is saved as a downstream object of the inlet
                            self.subBasinDict[iDSub].add_downstreamObj(self.retentionBasinDict[element])
                            # The inlet is linked as an inlet of the RB
                            self.retentionBasinDict[element].add_inlet(self.subBasinDict[iDSub])
                            # If the inlet is a subbasin which has no inlets, it is added to the 1st level of the topo tree.
                            # This procedure can be carried out as haveInlets have already been determined for all subbasin
                            # in the creation of the objects.
                            if(not(self.subBasinDict[iDSub].haveInlets)):
                                self.subBasinDict[iDSub].isLeveled = True
                                self.topologyDict['Level 1'][tmpString[i]] = self.subBasinDict[iDSub]
                            # Else the level of the subbasin in the topo tree is incremented (set to 2 if the tree is correct).
                            else:
                                self.subBasinDict[iDSub].increment_level()
                        # 'J' can be a RB or a subbasin
                        elif tmpString[i][0] == 'J':
                            # This variable count the number of iteration to see if all are used.
                            nbInter += 1
                            # if the inlet is a subbasin:
                            if(self.paramsTopology.myparams[tmpString[i]]['type']['value'] == 'Subbasin'):
                                nbSub += 1
                                iDSub = int(self.paramsTopology.myparams[tmpString[i]]['number']['value'].replace('ss', ''))
                                # A same subbasin cannot be used twice
                                if(self.subBasinDict[iDSub].alreadyUsed):
                                    print("ERROR: a subbasin has already been used. Please check the topology file!")
                                    sys.exit()
                                # Add the RB as the dowstream object of the inlet
                                self.subBasinDict[iDSub].add_downstreamObj(self.retentionBasinDict[element])
                                # Add inlet
                                self.retentionBasinDict[element].add_inlet(self.subBasinDict[iDSub])
                            # if the inlet is a RB:  
                            elif(self.paramsTopology.myparams[tmpString[i]]['type']['value'] == 'RB'):
                                # A RB cannot be used used twice
                                if(self.retentionBasinDict[tmpString[i]].alreadyUsed):
                                    print("ERROR: this RB was already used! Please check the topo file.")
                                    sys.exit()
                                self.retentionBasinDict[tmpString[i]].add_downstreamObj(self.retentionBasinDict[element])
                                self.retentionBasinDict[element].add_inlet(self.retentionBasinDict[tmpString[i]])
                            else:
                                print("This type of intersection is not recognised. Please check your topo file.")
                                sys.exit()
                        else:
                            print("This type of inlet is not recognised. Please check your topo file.")
                            sys.exit()
                # Case 2 : same procedure but for the flux entering the directly in RB
                if('direct inside RB' in self.paramsTopology.myparams[element]):
                    tmpString = self.paramsTopology.myparams[element]['direct inside RB']['value'].split(',')
                    for i in range(len(tmpString)):
                        tmpString[i]= tmpString[i].strip()
                        # Save the dowstream link of each element in the dictionnary
                        if tmpString[i][0:2] == 'ss' :
                            nbSub += 1
                            iDSub =  int(tmpString[i].replace('ss', ''))
                            if(self.subBasinDict[iDSub].alreadyUsed):
                                print("ERROR: a subbasin has already been used. Please check the topology file!")
                                sys.exit()
                            self.subBasinDict[iDSub].add_downstreamObj(self.retentionBasinDict[element])
                            self.retentionBasinDict[element].add_directFluxObj(self.subBasinDict[iDSub])
                            if(not(self.subBasinDict[iDSub].haveInlets)):
                                self.subBasinDict[iDSub].isLeveled = True
                                self.topologyDict['Level 1'][tmpString[i]] = self.subBasinDict[iDSub]
                            else:
                                self.subBasinDict[iDSub].increment_level()
                        elif tmpString[i][0] == 'J':
                            nbInter += 1
                            if(self.paramsTopology.myparams[tmpString[i]]['type']['value'] == 'Subbasin'):
                                nbSub += 1
                                iDSub = int(self.paramsTopology.myparams[tmpString[i]]['number']['value'].replace('ss', ''))
                                if(self.subBasinDict[iDSub].alreadyUsed):
                                    print("ERROR: a subbasin has already been used. Please check the topology file!")
                                    sys.exit()
                                self.subBasinDict[iDSub].add_downstreamObj(self.retentionBasinDict[element])
                                self.retentionBasinDict[element].add_directFluxObj(self.subBasinDict[iDSub])

                            elif(self.paramsTopology.myparams[tmpString[i]]['type']['value'] == 'RB'):
                                if(self.retentionBasinDict[tmpString[i]].alreadyUsed):
                                    print("ERROR: a RB has aleady been used! Please check your topo file.")
                                    sys.exit()
                                self.retentionBasinDict[tmpString[i]].add_downstreamObj(self.retentionBasinDict[element])
                                self.retentionBasinDict[element].add_directFluxObj(self.retentionBasinDict[tmpString[i]])
                            
                            else:
                                print("This type of intersection is not recognised. Please check your topo file.")
                                sys.exit()
                        else:
                            print("This type of inlet is not recognised. Please check your topo file.")
                            sys.exit()
            # If the intersection is a subbasin, same procedure as for the RB, exept that no direct flux 
            # are considered anymore.
            elif(self.paramsTopology.myparams[element]['type']['value'] == 'Subbasin'):
                elementId =  int(self.paramsTopology.myparams[element]['number']['value'].replace('ss', ''))
                tmpString = self.paramsTopology.myparams[element]['inlets']['value'].split(',')
                # If there are no inlet labelled by "--", add it on the first level
                if(len(tmpString)==1 and tmpString[0].strip()=='--'):
                    # self.topologyDict['Level 1'][element] = self.subBasinDict[elementId]
                    nbInter += 1 
                    continue

                for i in range(len(tmpString)):
                    tmpString[i]= tmpString[i].strip()
                    # Save the dowstream link of each element in the dictionnary
                    if tmpString[i][0:2] == 'ss' :
                        nbSub += 1
                        iDSub =  int(tmpString[i].replace('ss', ''))
                        if(self.subBasinDict[iDSub].alreadyUsed):
                            print("ERROR: a subbasin has already been used. Please check the topology file!")
                            sys.exit()
                        self.subBasinDict[iDSub].add_downstreamObj(self.subBasinDict[elementId])
                        self.subBasinDict[elementId].add_inlet(self.subBasinDict[iDSub])
                        if(not(self.subBasinDict[iDSub].haveInlets)):
                            self.subBasinDict[iDSub].isLeveled = True
                            self.topologyDict['Level 1'][tmpString[i]] = self.subBasinDict[iDSub]
                        else:
                            self.subBasinDict[iDSub].increment_level()
                    elif tmpString[i][0] == 'J':
                        nbInter += 1
                        if(self.paramsTopology.myparams[tmpString[i]]['type']['value'] == 'Subbasin'):
                            nbSub += 1
                            iDSub = int(self.paramsTopology.myparams[tmpString[i]]['number']['value'].replace('ss', ''))
                            if(self.subBasinDict[iDSub].alreadyUsed):
                                print("ERROR: a subbasin has already been used. Please check the topology file!")
                                sys.exit()
                            self.subBasinDict[iDSub].add_downstreamObj(self.subBasinDict[elementId])
                            self.subBasinDict[elementId].add_inlet(self.subBasinDict[iDSub])
                            if(not(self.subBasinDict[iDSub].haveInlets)):
                                self.subBasinDict[iDSub].isLeveled = True
                                self.topologyDict['Level 1'][tmpString[i]] = self.subBasinDict[iDSub]
                            elif(self.subBasinDict[iDSub].myLevel == 1):
                                self.subBasinDict[iDSub].increment_level()
                        elif(self.paramsTopology.myparams[tmpString[i]]['type']['value'] == 'RB'):
                            if(self.retentionBasinDict[tmpString[i]].alreadyUsed):
                                print("ERROR: a RB has already been used! Please check your topo file.")
                                sys.exit()
                            self.retentionBasinDict[tmpString[i]].add_downstreamObj(self.subBasinDict[elementId])
                            self.subBasinDict[elementId].add_inlet(self.retentionBasinDict[tmpString[i]])
                        else:
                            print("This type of intersection is not recognised. Please check your topo file.")
                            sys.exit()
                    else:
                        print("This type of inlet is not recognised. Please check your topo file.")
                        sys.exit()

        # Necessary but not sufficent condition for the Catchment network to be valid. 
        # Second verification in the TopoDict construction
        if(not(nbSub==self.nbSubBasin or nbSub==self.nbSubBasin-1) or nbInter==0):
            print("ERROR: all the subbasins or junctions are not used in the Catchment network! Please check your topo file.")
            sys.exit()
            


    def complete_topoDict(self):
        """ Procedure that finish to complete the topo tree.
            Before calling this procedure, only the first level were completed in self.link_objects().

            Modified internal variables: self.topologyDict

            Strategy:
                - We save the element on a certain level if all his inlets have inferior levels.

            TO DO: Add a test that counts the number of subbasins and check if the number is right or not
                    -> take into account the fact that a subbasin can be the last element in this computation.
        """
        toContinue = True   # variable used to stop the while loop
        # As the first level is already completed, we begin at level 2
        if(self.nbSubBasin==1):
            return
        level = 2
        while(toContinue):
            levelName = 'Level '+ str(level)
            self.topologyDict[levelName] = {}
            # element : name to search in the dict topo et catchment
            for element in self.topologyDict['Level '+str(level-1)]:
                # If one element in the previous level does not have a downstream
                # => It's the outlet of the Cachtment (as 1! outlet is possible in a same catchment)
                # => The level in the dictionnary is removed 
                # => Stop the loop
                if(self.catchmentDict[element].downstreamObj is None):
                    toContinue = False
                    del self.topologyDict[levelName]
                    break
                
                if(self.catchmentDict[element].downstreamObj.myLevel > level):
                    continue
                # iInlet : index of the inlet
                okLevel = True
                # We loop on the inlets of the downstream element:
                    # if: at least 1 element as the same or higher level as the current one 
                        # => increment level of the downstream element
                        # => We go another element on level-1
                    # else: we save the downstream element in topo tree on the 'level' branch
                for iInlet in range(len(self.catchmentDict[element].downstreamObj.intletsObj)):
                    if(self.catchmentDict[element].downstreamObj.intletsObj[iInlet].myLevel >= level):
                        self.catchmentDict[element].downstreamObj.increment_level()
                        okLevel = False
                        break
                    if(self.catchmentDict[element].downstreamObj.intletsObj[iInlet].isLeveled == False):
                        self.catchmentDict[element].downstreamObj.increment_level()
                        okLevel = False
                        break
                
                if(type(self.catchmentDict[element].downstreamObj) == RetentionBasin):
                    if(len(self.catchmentDict[element].downstreamObj.directFluxObj) != 0):
                        for iInlet in range(len(self.catchmentDict[element].downstreamObj.directFluxObj)):
                            if(self.catchmentDict[element].downstreamObj.directFluxObj[iInlet].myLevel >= level):
                                self.catchmentDict[element].downstreamObj.increment_level()
                                okLevel = False
                                break
                            if(self.catchmentDict[element].downstreamObj.directFluxObj[iInlet].isLeveled == False):
                                self.catchmentDict[element].downstreamObj.increment_level()
                                okLevel = False
                                break
                # Here all the inlets are on inferior level
                if(okLevel):
                    tmpID = self.catchmentDict[element].downstreamObj.iD
                    self.topologyDict[levelName][tmpID] = self.catchmentDict[tmpID]
                    self.catchmentDict[tmpID].isLeveled = True
            level += 1
                

              
    def construct_hydro(self):
        """ This procedure will use the topo tree to build the hydrographs of all elements

            Internal variable changed: self.catchmentDict
        """
        for i in range(1, len(self.topologyDict)+1):
            tmpLevel = 'Level '+ str(i)
            for element in self.topologyDict[tmpLevel]:
                self.catchmentDict[element].compute_hydro()



    def read_Jsonfile(self, fileName):
        "Function which reads a json file as input"
        with open(fileName, 'r') as json_file:
            data = json.load(json_file)
            print("data = ", data)
        return data



    def save_ExcelFile(self):
        "Procedure that saves the data in an Excel file."
        # Writes subbasins' hydrographs
        # writer = pd.ExcelWriter("C:/Users/Christophe Dessers/Documents/Cours ULG/Doctorat/Python/PostProcessing/Data/"+"Data.xlsx", engine = 'xlsxwriter')
        writer = pd.ExcelWriter(self.workingDir+"PostProcess/Data_outflow.xlsx", engine = 'xlsxwriter')
        columnNames = ['Time [s]', 'Real hydrograph [m^3/s]', 'Raw hydrograph [m^3/s]']
        for element in self.subBasinDict:
            excelData = np.zeros((len(self.time),3))
            sheetName = self.subBasinDict[element].name
            if(len(sheetName)>30):
                sheetName = sheetName[:30]
            for i in range(len(self.time)):
                excelData[i][0] = self.time[i]
                excelData[i][1] = self.subBasinDict[element].outFlow[i]
                excelData[i][2] = self.subBasinDict[element].outFlowRaw[i]
            df = pd.DataFrame(excelData, columns=columnNames)
            df.to_excel(writer , sheet_name= sheetName[0:min(len(sheetName),30)])
        # Writes the RB hydrographs
        for element in self.retentionBasinDict:
            excelData = np.zeros((len(self.time),3))
            sheetName = self.retentionBasinDict[element].name
            for i in range(len(self.time)):
                excelData[i][0] = self.time[i]
                excelData[i][1] = self.retentionBasinDict[element].outFlow[i]
                excelData[i][2] = self.retentionBasinDict[element].outFlowRaw[i]
            df = pd.DataFrame(excelData, columns=columnNames)
            df.to_excel(writer , sheet_name= sheetName)
        writer.save()
        writer.close()



    def save_ExcelFile_noLagTime(self):
        "Procedure that saves the data in an Excel file."
        # Writes subbasins' hydrographs
        # writer = pd.ExcelWriter("C:/Users/Christophe Dessers/Documents/Cours ULG/Doctorat/Python/PostProcessing/Data/"+"Data.xlsx", engine = 'xlsxwriter')
        writer = pd.ExcelWriter(self.workingDir+"PostProcess/Data_outflow_noLagTime.xlsx", engine = 'xlsxwriter')
        columnNames = ['Time [s]', 'Real hydrograph [m^3/s]', 'Raw hydrograph [m^3/s]']
        for element in self.subBasinDict:
            excelData = np.zeros((len(self.time),3))
            sheetName = self.subBasinDict[element].name
            if(len(sheetName)>30):
                sheetName = sheetName[:30]
            tmpOutFlow = self.subBasinDict[element].get_outFlow_noDelay()
            tmpOutFlowRaw = self.subBasinDict[element].get_outFlowRaw_noDelay()
            for i in range(len(self.time)):
                excelData[i][0] = self.time[i]
                excelData[i][1] = tmpOutFlow[i]
                excelData[i][2] = tmpOutFlowRaw[i]
            df = pd.DataFrame(excelData, columns=columnNames)
            df.to_excel(writer , sheet_name= sheetName[0:min(len(sheetName),30)])
        # Writes the RB hydrographs
        for element in self.retentionBasinDict:
            excelData = np.zeros((len(self.time),3))
            sheetName = self.retentionBasinDict[element].name
            tmpOutFlow = self.retentionBasinDict[element].get_outFlow_noDelay()
            tmpOutFlowRaw = self.retentionBasinDict[element].get_outFlowRaw_noDelay()
            for i in range(len(self.time)):
                excelData[i][0] = self.time[i]
                excelData[i][1] = tmpOutFlow[i]
                excelData[i][2] = tmpOutFlowRaw[i]
            df = pd.DataFrame(excelData, columns=columnNames)
            df.to_excel(writer , sheet_name= sheetName)
        writer.save()
        writer.close()


        
    def save_ExcelFile_V2(self):
        "Procedure that saves the data in an Excel file."
        # Writes subbasins' hydrographs
        # writer = pd.ExcelWriter("C:/Users/Christophe Dessers/Documents/Cours ULG/Doctorat/Python/PostProcessing/Data/"+"Data.xlsx", engine = 'xlsxwriter')
        writer = pd.ExcelWriter(self.workingDir+"PostProcess/Data_myHydro.xlsx", engine = 'xlsxwriter')
        nbSub = len(self.subBasinDict)
        excelData = np.zeros((len(self.time),nbSub+1))
        columnNames = []

        columnNames.append("Times")
        for element in self.subBasinDict:
            
            # excelData[0][element] = self.subBasinDict[element].x
            # excelData[1][element] = self.subBasinDict[element].y
            columnNames.append(self.subBasinDict[element].name)
            for i in range(len(self.time)):
                excelData[i][0] = self.time[i]
                excelData[i][element] = self.subBasinDict[element].myHydro[i]
        df = pd.DataFrame(excelData, columns=columnNames)      
        df.to_excel(writer, sheet_name="Hydrographs")

        excelData = np.zeros((nbSub,2))
        coordinateNames = ["x", "y"]
        columnNames.pop(0)
    
        for element in self.subBasinDict:
            excelData[element-1][0] = self.subBasinDict[element].x
            excelData[element-1][1] = self.subBasinDict[element].y

        df = pd.DataFrame(excelData, columns=coordinateNames, index=columnNames)   
        df.to_excel(writer, sheet_name="Outlet coordinates")

        writer.save()
        writer.close()
    


    def save_characteristics(self):
        "Procedure that saves the data in an Excel file."
        # Writes subbasins' main characteristics
        # writer = pd.ExcelWriter("C:/Users/Christophe Dessers/Documents/Cours ULG/Doctorat/Python/PostProcessing/Data/"+"Data.xlsx", engine = 'xlsxwriter')
        writer = pd.ExcelWriter(self.workingDir+"PostProcess/Basins_Characteristics.xlsx", engine = 'xlsxwriter')
        columnNames = ['Characteristic', 'unit']
        # excelData = np.zeros((16,self.nbSubBasin+2))
        excelData = [[] for i in range(self.nbSubBasin+2)]
        iBasin = 1
        for level in self.topologyDict:
            for curBasin in self.topologyDict[level]:
                if(type(self.topologyDict[level][curBasin])!=SubBasin):
                    continue

                if(iBasin==1):
                    excelData[0].append("Coord")
                    excelData[0].append("x")
                    excelData[1].append("Coord")
                    excelData[1].append("y")
                    iChar = 2
                    for name in self.topologyDict[level][curBasin].mainCharactDict:
                        excelData[iChar].append(name)
                        excelData[iChar].append(self.topologyDict[level][curBasin].mainCharactDict[name]["unit"])
                        
                        iChar += 1

                columnNames.append(self.topologyDict[level][curBasin].name)
                iChar = 2
                excelData[0].append(self.topologyDict[level][curBasin].x)
                excelData[1].append(self.topologyDict[level][curBasin].y)                
                for curChar in self.topologyDict[level][curBasin].mainCharactDict:
                    excelData[iChar].append(self.topologyDict[level][curBasin].mainCharactDict[curChar]['value'])
                    iChar += 1                    
                iBasin += 1

        df = pd.DataFrame(excelData, columns=columnNames)
        df.to_excel(writer)
        writer.save()
        writer.close()



    def read_dbfFile(self, fileName):
        dbfDict = DBF(fileName, load=True)
        return dbfDict



    def init_hyetoDict(self):
        """ Procedure that saves the all the hyeto data of the Catchment in a dictionnary
            Internal variables modified: self.hyetoDict

            Structure du dictionnaire
            self.hyetoDict:
                - Ordered To Nb: self.hyetoDict['Ordered To Nb'][nb] = iD
                  , iD = hyeto nb of the file to read in the folder "Whole_basin". E.g.: the file "[iD]evap.hyeto"
                  , nb = hyeto number sorted from 1 to nbHyeto. E.g.: if iD=['2', '5', '7'] => self.hyetoDict['Ordered To Nb'][2] = '5'
                - Hyetos : self.hyetoDict['Hyetos'][nb]
                    - time: time array read in the .hyeto file
                    - rain: rain array read in the .hyeto file

        TO DO: Consider a more general way to detect .dbf files. E.G. when the data are read in NetCDF files.
        """

        # Read the DBF file to save all the "Ordered To Nb" in the dictionnary
        fileName = self.workingDir + "Whole_basin/Rain_basin_geom.vec.dbf"
        if(os.path.exists(fileName)):
            dbfDict = self.read_dbfFile(fileName)
            self.hyetoDict['Ordered To Nb'] = {}
            self.hyetoDict['Hyetos'] = {}

            for i in range(len(dbfDict.records)):
                iDsorted = i + 1
                iDHyeto = dbfDict.records[i]['data']
                self.hyetoDict['Ordered To Nb'][iDsorted] = iDHyeto

            # Read all the .hyeto file to save the time and rain arrays
            beginFileName = self.workingDir + "Whole_basin/"
            endFileName = "rain.hyeto"
            for element in self.hyetoDict['Ordered To Nb']:
                nbToRead = self.hyetoDict['Ordered To Nb'][element]
                fileName = beginFileName + nbToRead + endFileName
                [time, rain] = self.get_hyeto(fileName)
                self.hyetoDict['Hyetos'][element] = {}
                self.hyetoDict['Hyetos'][element]['time'] = time
                self.hyetoDict['Hyetos'][element]['rain'] = rain
        else:
            print("WARNING: could not find any dbf file! ")
            time_mod.sleep(5)



    def add_rainToAllObjects(self):
        "Add rain and hyetographs to all subbasins"

        # for element in self.subBasinDict:
        #     timeTest, _ = self.subBasinDict[element].add_rain(self.workingDir)
        #     if not(np.array_equal(timeTest,self.time)):
        #         print("ERROR: the time arrays are different!")
        #     self.subBasinDict[element].add_hyeto(self.workingDir, self.hyetoDict)
        txt = "Level "
        for i in range(1,len(self.topologyDict)+1):
            indexName = txt + str(i)
            for element in self.topologyDict[indexName]:
                timeTest = self.topologyDict[indexName][element].add_rain(self.workingDir, tzDelta=datetime.timedelta(hours=self.tz))
                if not(np.array_equal(timeTest,self.time)):
                    print("ERROR: the time arrays are different!")
                if type(self.topologyDict[indexName][element]) == SubBasin:
                    self.topologyDict[indexName][element].add_hyeto(self.workingDir, self.hyetoDict)



    def plot_intersection(self):
        "This procedure will plot all the subbasins or RB with level>1 in the topo tree."
        txt = "Level "
        plot_raw = True
        if(len(self.retentionBasinDict)==0):
            plot_raw = False
        for i in range(2, len(self.topologyDict)+1):
            indexName = txt + str(i)
            for element in self.topologyDict[indexName]:
                self.topologyDict[indexName][element].plot(self.workingDir,plot_raw)
        plt.show()



    def plot_allSub(self):
        "This procedure plots the hydrographs and hyetographs of all subbasins"
        for element in self.subBasinDict:
            self.subBasinDict[element].plot_myBasin()
        plt.show()



    def draw_flowChart(self, flowchart):
        '''This procedure save and plot a flowchart representing the topo tree
            input: - flowchart: graphviz.Digraph Object -> modified at the end

        '''

        # Creation of the flowchart nodes -> first iteration of the topo tree.
        for level in range(1, len(self.topologyDict)+1):
            nameLevel = 'Level ' + str(level)
            with flowchart.subgraph() as s:
                s.attr(rank='same')
                for element in self.topologyDict[nameLevel]:
                    nodeName = self.topologyDict[nameLevel][element].name
                    if(type(self.topologyDict[nameLevel][element])==RetentionBasin):
                        shapeName = 'box'
                    elif(type(self.topologyDict[nameLevel][element])==SubBasin):
                        shapeName = 'circle'
                        nodeID = self.topologyDict[nameLevel][element].iD
                        sortNodeID = str(self.topologyDict[nameLevel][element].iDSorted)
                        if(nodeID != nodeName.replace(' ', '')):
                            nodeName += ' ('+nodeID+')'
                        nodeName += ' [sub'+sortNodeID+']'
                    s.node(nodeName, shape=shapeName)
        # Creation of the flowchart edges -> second iteration of the topo tree.
        for level in range(1, len(self.topologyDict)):
            nameLevel = 'Level ' + str(level)
            for element in self.topologyDict[nameLevel]:
                nodeName = self.topologyDict[nameLevel][element].name
                if(type(self.topologyDict[nameLevel][element])==SubBasin):
                    nodeID = self.topologyDict[nameLevel][element].iD
                    sortNodeID = str(self.topologyDict[nameLevel][element].iDSorted)
                    if(nodeID != nodeName.replace(' ', '')):
                        nodeName += ' ('+nodeID+')'
                    nodeName += ' [sub'+sortNodeID+']'
                downName = self.topologyDict[nameLevel][element].downstreamObj.name
                if(type(self.topologyDict[nameLevel][element].downstreamObj)==SubBasin):
                    nodeID = self.topologyDict[nameLevel][element].downstreamObj.iD
                    sortNodeID = str(self.topologyDict[nameLevel][element].downstreamObj.iDSorted)
                    if(nodeID != downName.replace(' ', '')):
                        downName += ' ('+nodeID+')'
                    downName += ' [sub'+sortNodeID+']'
                flowchart.edge(nodeName, downName)



    def make_stat_distributionOfslope(self):
        """ This procedure plot the stat distribution of slopes.
        """
        print("Procedure for slope's stat distribution ongoing")
        slope_wolf_array = WolfArray(self.workingDir + "Characteristic_maps/Drainage_basin.slope")
        slope_array = []
        for i in range(slope_wolf_array.nbx):
            for j in range(slope_wolf_array.nby):
                element = slope_wolf_array.get_value_from_ij(i,j)
                if element == float('inf'):
                    continue
                slope_array.append(element)
        slope_arraySort = np.sort(slope_array, axis = None)
        maxSlope = slope_arraySort[len(slope_arraySort)-1]
        myBins = np.arange(0,maxSlope, 0.0001)
        slopeHisto = np.histogram(slope_arraySort, bins=myBins, density=True)

        return slopeHisto, slope_arraySort
        print("Hello!")



    def make_stat_distributionOfTime(self):
        """ This procedure plot the stat distribution of slopes.
        """
        print("Procedure for slope's stat distribution ongoing")
        slope_wolf_array = WolfArray(self.workingDir + "Characteristic_maps/Drainage_basin.slope")
        slope_array = []
        for i in range(slope_wolf_array.nbx):
            for j in range(slope_wolf_array.nby):
                element = slope_wolf_array.get_value_from_ij(i,j)
                if element == float('inf'):
                    continue
                slope_array.append(element)
        slope_arraySort = np.sort(slope_array, axis = None)
        maxSlope = slope_arraySort[len(slope_arraySort)-1]
        myBins = np.arange(0,maxSlope, 0.0001)
        slopeHisto = np.histogram(slope_arraySort, bins=myBins, density=True)

        return slopeHisto, slope_arraySort
        print("Hello!")



    def check_massConservation(self):
        """ This procedure check whether the mass conservation is verified ot not.            
        """
        print("Checking the mass conservation ...")

        cumulRain = 0.0
        cumulFlow = 0.0
        

        nbLevels = len(self.topologyDict)
        
        # CAUTION !!!!!!hardcoded value for the Ourthe Basin !!!!!!!!
        surface = 1615.02000*(1000.0)**2
        ds = 10000.0
        not_used_rain = 1.45312406886231*ds
        


        tmpCount = 0
        nameLastLevel = 'Level '+ str(nbLevels)
        for element in self.topologyDict[nameLastLevel]:
            nbElements = len(self.topologyDict[nameLastLevel][element].rain)
            plotCumulRain = np.zeros(nbElements)
            plotCumulFlow = np.zeros(nbElements)

            cumulRain = np.sum(self.topologyDict[nameLastLevel][element].rain)      # [mm/h]
            cumulFlow = np.sum(self.topologyDict[nameLastLevel][element].outFlow)   # [m^3/s]
            plotCumulRain[0] = self.topologyDict[nameLastLevel][element].rain[0]*self.deltaT
            plotCumulFlow[0] = self.topologyDict[nameLastLevel][element].outFlow[0]*self.deltaT
            for i in range(1,nbElements):
                plotCumulRain[i] = plotCumulRain[i-1] + self.topologyDict[nameLastLevel][element].rain[i]*self.deltaT
                plotCumulFlow[i] = plotCumulFlow[i-1] + self.topologyDict[nameLastLevel][element].outFlow[i]*self.deltaT

        cumulRain = cumulRain/(1000.0*3600.0)*surface
        cumulFlow = cumulFlow+not_used_rain
        plotCumulRain = plotCumulRain/(1000.0*3600.0)*surface

        # ~~~~~~~~~~~~~~~~~~
        x = (self.time/(3600.0*24.0*365.0))+2000.0
        
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
        plt.ylabel('Volume cumulé [m³]', fontproperties=font11)
        plt.legend(loc="best")
        plt.title(self.name + " Conservation du volume", fontproperties=font14)

        y = plotCumulRain
        plt.plot(x, y, label = 'pluie')
        y = plotCumulFlow
        plt.plot(x, y, label = 'volume écoulé')
        plt.xlim(2000, 2003)
        plt.xticks([2000, 2001, 2002, 2003])
        plt.legend(prop=font11)
        plt.savefig(self.workingDir+'PostProcess/Conservation_volume_'+self.name+'.pdf')
        print("Is it the correct mass?")
        plt.show()
        print("Hello!")



    def copy(self):

        copiedObj = Catchment(self.name, self.workingDir,False, True, _initWithResults=False)

        copiedObj.time = self.time.copy()                                      
        copiedObj.deltaT = self.deltaT
        copiedObj.dateBegin = copy.deepcopy(self.dateBegin)
        copiedObj.dateEnd = copy.deepcopy(self.dateEnd)                                             
        copiedObj.myModel = self.myModel
        copiedObj.nbCommune = self.nbCommune
        copiedObj.nbSubBasin = self.nbSubBasin
        copiedObj.hyeto = copy.deepcopy(self.hyeto)
        copiedObj.catchmentDict = copy.deepcopy(self.catchmentDict)
        copiedObj.subBasinDict = copy.deepcopy(self.subBasinDict)
        copiedObj.retentionBasinDict = copy.deepcopy(self.retentionBasinDict)
        copiedObj.topologyDict = copy.deepcopy(self.topologyDict)
        copiedObj.dictIdConversion = copy.deepcopy(self.dictIdConversion)
        copiedObj.hyetoDict = copy.deepcopy(self.hyetoDict)
        copiedObj.intersection = copy.deepcopy(self.intersection)

        return copiedObj
       