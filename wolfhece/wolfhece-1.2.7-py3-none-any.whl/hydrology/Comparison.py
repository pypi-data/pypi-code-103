import sys                              # module to stop the program when an error is encountered
import os
import matplotlib.pyplot as plt
import numpy as np
from numpy.core.arrayprint import set_string_function

if not '_' in globals()['__builtins__']: #Test de la présence de la fonction de traduction i18n "gettext" et définition le cas échéant pour ne pas créer d'erreur d'exécution
    import gettext
    _=gettext.gettext

from .Catchment import *

class Comparison:
    ''' 
    This class contains several Catchment objects and all the procedures
    to produce plots that can compare different results of these Catchments.
    '''

    ## Constructor
    def __init__(self, workingDir, dictCatchment, dictToCompar):
        
        # ===========
        #
        #  

        ## @var workingDir The path of the working directory
        self.workingDir = workingDir + 'PostProcess_Comparison/'

        ## Dictionary containing all the objects Catchment:
        #  @var dictCatchment dictionnary containing: 'Title' and 'Object'
        #  'Title': the name that one wants to give to the element on graphs
        #  'Object': The Catchment object containing all the information of the Catchment.
        self.myCatchments = dictCatchment


        ## @var dictToCompar 
        # Dictionary containing:
        # - 1: if the plot function is used
        # - 0: otherwise
        self.dictToCompar = dictToCompar
        

        # ==========================================================================================

        # Creation of the PostProcess directory
        # It will contain all the the saved results.
        
        if not os.path.exists(self.workingDir):
            try:
                os.mkdir(self.workingDir)
            except OSError:
                print ("Creation of the directory %s failed" % self.workingDir)
            else:
                print ("Successfully created the directory %s" % self.workingDir)


        # Verification that the number of Catchments to compare is greater than 1
        if(len(self.myCatchments)<=1):
            print('ERROR: Cannot compare less than 2 Catchments')
            sys.exit()

    
    def compare_now(self):
        
        # Check and run all the functions to use
        if(int(self.dictToCompar['hydro subbasin']['value']) == 1):
            self.hydro_subbasin()
        if(int(self.dictToCompar['hydro junction']['value']) == 1):
            self.hydro_junction()
        if(int(self.dictToCompar['hydro final']['value']) == 1):
            self.hydro_final()
        
    
    def hydro_subbasin(self):
        print("Comparison of all subbasin ...")

        # Test that the number of subbasins are the same
        nbSubBasins=len(self.myCatchments['Catchment 1']['Object'].subBasinDict)
        for i in range(2, len(self.myCatchments)+1):
            txtTmp = 'Catchment ' + str(i)
            tmpNb = len(self.myCatchments[txtTmp]['Object'].subBasinDict)
            if(tmpNb!=nbSubBasins):
                print("ERROR: These Catchments cannot be compared as their number of subbasins are not the same!")
                sys.exit()
            

        for subId in range(1,tmpNb+1):
            # Figure Rain on a first y axis
            fig,ax1=plt.subplots()
            ax1.set_xlabel('Temps [années]')
            ax1.set_ylabel('Débits [mm/s]',color='k') #Color express in %RGB: (1,1,1)
            # ax1.set_ylim(0, self.myHydro.max()*2)
            # ax1.hist(data1,color=(0,0,1),edgecolor='black',linewidth=1.2)
            max_= 0
            for element in self.myCatchments:
                title = self.myCatchments[element]['Title']
                pointer = self.myCatchments[element]['Object'].subBasinDict[subId]
                x = pointer.time/(3600.0*24*365)+2000    # [years]
                y1 = pointer.myHydro
                y2 = pointer.rain
                if(y1.max()>max_):
                    max_ = y1.max()
                ax1.set_ylim(0, max_*2)
                ax1.set_xticks([2000, 2001, 2002, 2003])
                ax1.plot(x,y1,'--',label=title)
            ax1.tick_params(axis='y',labelcolor='k')

            # Figure Hydro on a second y axis
            ax2=ax1.twinx()
            ax2.set_ylabel('Précipitations [m³/s]',color='b')
            ax2.set_ylim(y2.max()*3, 0)
            ax2.plot(x,y2,color='b')
            ax2.fill_between(x, y2, 0, color='b')
            ax2.tick_params(axis='y',labelcolor='b')
            fig.tight_layout()
            handles, labels = ax1.get_legend_handles_labels()
            fig.legend(handles, labels)
            plt.savefig(self.workingDir+'/Subbasin_'+str(subId)+'_Compar'+'.pdf')


    def hydro_junction(self):
        print("Comparison of all junctions ...")


        # # Test that the number of subbasins are the same
        # nbJunction=len(self.myCatchments['Catchment 1']['Object'].intersection)
        # for i in range(2, len(self.myCatchments)+1):
        #     txtTmp = 'Catchment ' + str(i)
        #     tmpNb = len(self.myCatchments[txtTmp]['Object'].intersection)
        #     if(tmpNb!=nbJunction):
        #         print("ERROR: These Catchments cannot be compared as their number of subbasins are not the same!")
        #         sys.exit()
            

        # for subId in range(1,tmpNb+1):
        #     # Figure Rain on a first y axis
        #     fig,ax1=plt.subplots()
        #     ax1.set_xlabel('Temps [h]')
        #     ax1.set_ylabel('Débits [mm/s]',color='k') #Color express in %RGB: (1,1,1)
        #     # ax1.set_ylim(0, self.myHydro.max()*2)
        #     # ax1.hist(data1,color=(0,0,1),edgecolor='black',linewidth=1.2)
        #     max_= 0
        #     for element in self.myCatchments:
        #         title = self.myCatchments[element]['Title']
        #         pointer = self.myCatchments[element]['Object'].intersection[subId]
        #         x = pointer.time/3600.0    # [h]
        #         y1 = pointer.myHydro
        #         y2 = pointer.rain
        #         if(y1.max()>max_):
        #             max_ = y1.max()
        #         ax1.set_ylim(0, max_*2)
        #         ax1.plot(x,y1,label=title)
        #     ax1.tick_params(axis='y',labelcolor='k')

        #     # Figure Hydro on a second y axis
        #     ax2=ax1.twinx()
        #     ax2.set_ylabel('Précipitations [m³/s]',color='b')
        #     ax2.set_ylim(y2.max()*3, 0)
        #     ax2.plot(x,y2,color='b')
        #     ax2.fill_between(x, y2, 0, color='b')
        #     ax2.tick_params(axis='y',labelcolor='b')
        #     fig.tight_layout()
        #     handles, labels = ax1.get_legend_handles_labels()
        #     fig.legend(handles, labels)
        #     plt.savefig(self.workingDir+'/Subbasin_'+str(subId)+'_Compar'+'.pdf')

    ## Caution the number of levels are not assumed to be the same here! This function can compare
    #  catchments with completely different topology
    def hydro_final(self):
        print("Comparison of the outlets ...")

        for element in self.myCatchments:
            self.myCatchments[element]['Object'].topologyDict[indexName][element].plot(self.workingDir)

            for i in range(2, len(self.myCatchments)+1):
                i_catchment = 'Catchment ' + str(i)
                nbLevels = len(self.myCatchments[i_catchment]['Object'].topologyDict)
                
                plot()
            

    def hyetos(self, catchColors=[], rangeRain=[], writeFile='', myTraits=None, beginDate=None, endDate=None, dt=None, yrangeData=[], \
                addData=[], dt_addData=[], beginDates_addData=[], endDates_addData=[],label_addData=[], color_addData=[], typeOfTraits_addData=[],cumulOrigin_addData=[]):
        '''
        TO DO : A Généraliser dans le cas où les sous-bassins n'ont pas le même nom et topologie !!!!!
        '''
        print("Comparison of the hyetos from all subbasins")

        if(beginDate==None):
            beginDate = []
            for idCatch in self.myCatchments:
                beginDate.append(self.myCatchments[idCatch]['Object'].dateBegin)
                # beginDate = self.myCatchments[idCatch]['Object'].dateBegin
                # break
            
        if(endDate==None):
            endDate = []
            for idCatch in self.myCatchments:
                endDate.append(self.myCatchments[idCatch]['Object'].dateEnd)
                # endDate = self.myCatchments[idCatch]['Object'].dateEnd
                # break
                
        if(dt==None):
            dt=[]
            for idCatch in self.myCatchments:
                dt.append(self.myCatchments[idCatch]['Object'].deltaT)


        basinNames = [] # contains all the names of the subbasin
        for idCatch in self.myCatchments:
            curCatch = self.myCatchments[idCatch]['Object']
            for nameBasin in curCatch.subBasinDict:
                if(not(nameBasin in basinNames)):
                    basinNames.append(nameBasin)


        nbCatchment = len(self.myCatchments)
        x_title = "Dates"


        if(catchColors==[]):
            tmpColors = np.random.rand(nbCatchment)
            for icolor in range(len(tmpColors)):
                catchColors.append(tmpColors[icolor])

        elif(len(catchColors)!=nbCatchment):
            print("ERROR: the number of catchments is not the same as the number of colors given")

        for nameBasin in basinNames:
            
            y1 = []
            y2 = []
            yLabels = []
            myTraits = []
            for idCatch in self.myCatchments:
                curCatch = self.myCatchments[idCatch]['Object']
                y1.append(curCatch.subBasinDict[nameBasin].myRain[:-1])

                dtH = curCatch.subBasinDict[nameBasin].deltaT/3600.0
                tmpCumul = datt.cumul_data(curCatch.subBasinDict[nameBasin].myRain[:-1], dtH, dtH)
                y2.append(tmpCumul)
                yLabels.append(curCatch.name)

                graph_title = curCatch.subBasinDict[nameBasin].name
                myTraits.append('-')


            nbAddData = 0
            if(addData!=[]):
                nbAddData = len(addData)
                for i in range(nbAddData):
                    y1.append(addData[i][:-1])
                    tmpY2 = datt.cumul_data(addData[i][:-1], dt_addData[i]/3600.0, dt_addData[i]/3600.0)
                    if(cumulOrigin_addData!=[]):
                        y2.append(tmpY2-cumulOrigin_addData[i])
                    else:
                        y2.append(tmpY2)
                    beginDate.append(beginDates_addData[i])
                    endDate.append(endDates_addData[i])
                    dt.append(dt_addData[i])
                    if(label_addData!=[]):
                        yLabels.append(label_addData[i])
                    if(color_addData!=[]):
                        catchColors.append(color_addData[i])
                    if(typeOfTraits_addData!=[]):
                        myTraits.append(typeOfTraits_addData[i])



            # Plot Rains
            yTitles = "Pluies [mm/h]"
            writeFileDef = writeFile + "_Rain_" + graph_title.replace(".","")
            ph.plot_hydro(nbCatchment+nbAddData, y1, x_title=x_title, y_titles=yTitles, beginDate=beginDate,endDate=endDate,dt=dt,graph_title=graph_title, \
                            y_labels=yLabels,rangeData=rangeRain,y_data_range=yrangeData,myColors=catchColors,typeOfTraits=myTraits,writeFile=writeFileDef)

            # Plot Cumulated rains
            yTitles = "Cumulated Rain [mm]"
            writeFileDef = writeFile + "_CumulRain_" + graph_title.replace(".","")
            ph.plot_hydro(nbCatchment+nbAddData, y2, x_title=x_title, y_titles=yTitles, beginDate=beginDate,endDate=endDate, dt=dt,graph_title=graph_title, \
                            y_labels=yLabels,rangeData=rangeRain,y_data_range=yrangeData,myColors=catchColors,typeOfTraits=myTraits,writeFile=writeFileDef)
            
            plt.show()



    def comparison_with_measures(self,addCatchment):

            print("TO DO")        
            sys.exit()
            
            x_range = [x_min,x_max]

            attemptName = "Comparaison Hydro"

            for element in testFroudeCatchment.subBasinDict:
                if(testFroudeCatchment.subBasinDict[element].name == "Chaudfontaine"):
                    stationName = "Chaudfontaine"
                    Qnat = naturalCatchment.subBasinDict[element].myHydro[:]
                    addData = []
                    addData.append(Qnat[:-1])
                    dtAddData = [testFroudeCatchment.deltaT]
                    beginDatesAddData = [testFroudeCatchment.dateBegin]
                    endDatesAddData = [testFroudeCatchment.dateEnd]
                    label_addData = ["BV avant modification du Froude"]
                    color_addData = ["y"]

                    testFroudeCatchment.subBasinDict[element].plot_outlet(Measures=RV.MeasuresChau,withEvap=False,rangeData=x_range,graph_title=stationName ,writeFile=writeDir+stationName+attemptName, withDelay=False)
                elif(testFroudeCatchment.subBasinDict[element].name == "Theux"):
                    stationName = "Theux"
                    Qnat = naturalCatchment.subBasinDict[element].myHydro[:]
                    addData = []
                    addData.append(Qnat[:-1])
                    dtAddData = [testFroudeCatchment.deltaT]
                    beginDatesAddData = [testFroudeCatchment.dateBegin]
                    endDatesAddData = [testFroudeCatchment.dateEnd]
                    label_addData = ["BV avant modification du Froude"]
                    color_addData = ["y"]
                    
                    testFroudeCatchment.subBasinDict[element].plot_outlet(Measures=RV.MeasuresTheu,withEvap=False,rangeData=x_range,graph_title=stationName,writeFile=writeDir+stationName+attemptName, withDelay=False)
                elif(testFroudeCatchment.subBasinDict[element].name == "SPIXHE"):
                    stationName = "SPIXHE"
                    Qnat = naturalCatchment.subBasinDict[element].myHydro[:]
                    addData = []
                    addData.append(Qnat[:-1])
                    dtAddData = [testFroudeCatchment.deltaT]
                    beginDatesAddData = [testFroudeCatchment.dateBegin]
                    endDatesAddData = [testFroudeCatchment.dateEnd]
                    label_addData = ["BV avant modification du Froude"]
                    color_addData = ["y"]

                    testFroudeCatchment.subBasinDict[element].plot_outlet(Measures=RV.MeasuresSpix,withEvap=False,rangeData=x_range,graph_title=stationName ,writeFile=writeDir+stationName+attemptName, withDelay=False)
                elif(testFroudeCatchment.subBasinDict[element].name == "Station Verviers"):
                    stationName = "Station Verviers"
                    Qnat = naturalCatchment.subBasinDict[element].myHydro[:]
                    addData = []
                    addData.append(Qnat[:-1])
                    dtAddData = [testFroudeCatchment.deltaT]
                    beginDatesAddData = [testFroudeCatchment.dateBegin]
                    endDatesAddData = [testFroudeCatchment.dateEnd]
                    label_addData = ["BV avant modification du Froude"]
                    color_addData = ["y"]

                    testFroudeCatchment.subBasinDict[element].plot_outlet(Measures=RV.MeasuresVerv,withEvap=False,rangeData=x_range,graph_title=stationName ,writeFile=writeDir+stationName+attemptName, withDelay=False)
                elif(testFroudeCatchment.subBasinDict[element].name == "Station Foret (Magne)"):
                    stationName = "Station Foret (Magne)"
                    Qnat = naturalCatchment.subBasinDict[element].myHydro[:]
                    addData = []
                    addData.append(Qnat[:-1])
                    dtAddData = [testFroudeCatchment.deltaT]
                    beginDatesAddData = [testFroudeCatchment.dateBegin]
                    endDatesAddData = [testFroudeCatchment.dateEnd]
                    label_addData = ["BV avant modification du Froude"]
                    color_addData = ["y"]

                    testFroudeCatchment.subBasinDict[element].plot_outlet(Measures=RV.MeasuresFor,withEvap=False,rangeData=x_range,graph_title=stationName ,writeFile=writeDir+stationName+attemptName, withDelay=False)
                elif(testFroudeCatchment.subBasinDict[element].name == "Polleur"):
                    stationName = "Polleur"
                    Qnat = naturalCatchment.subBasinDict[element].myHydro[:]
                    addData = []
                    addData.append(Qnat[:-1])
                    dtAddData = [testFroudeCatchment.deltaT]
                    beginDatesAddData = [testFroudeCatchment.dateBegin]
                    endDatesAddData = [testFroudeCatchment.dateEnd]
                    label_addData = ["BV avant modification du Froude"]
                    color_addData = ["y"]

                    testFroudeCatchment.subBasinDict[element].plot_outlet(Measures=RV.MeasuresPoll,withEvap=False,rangeData=x_range,graph_title=stationName ,writeFile=writeDir+stationName+attemptName, withDelay=False)
                elif(testFroudeCatchment.subBasinDict[element].name == "Belleheid"):
                    stationName = "Belleheid"
                    Qnat = naturalCatchment.subBasinDict[element].myHydro[:]
                    addData = []
                    addData.append(Qnat[:-1])
                    dtAddData = [testFroudeCatchment.deltaT]
                    beginDatesAddData = [testFroudeCatchment.dateBegin]
                    endDatesAddData = [testFroudeCatchment.dateEnd]
                    label_addData = ["BV avant modification du Froude"]
                    color_addData = ["y"]

                    testFroudeCatchment.subBasinDict[element].plot_outlet(Measures=RV.MeasuresBell,withEvap=False,rangeData=x_range,graph_title=stationName ,writeFile=writeDir+stationName+attemptName, withDelay=False)
                elif(testFroudeCatchment.subBasinDict[element].name == "Barrage Vesdre"):
                    stationName = "Barrage Vesdre"
                    Qnat = naturalCatchment.subBasinDict[element].myHydro[:]
                    addData = []
                    addData.append(Qnat[:-1])
                    dtAddData = [testFroudeCatchment.deltaT]
                    beginDatesAddData = [testFroudeCatchment.dateBegin]
                    endDatesAddData = [testFroudeCatchment.dateEnd]
                    label_addData = ["BV avant modification du Froude"]
                    color_addData = ["y"]

                    testFroudeCatchment.subBasinDict[element].plot_outlet(Measures=RV.MeasuresBVesIn,withEvap=False,rangeData=x_range,graph_title=stationName ,writeFile=writeDir+stationName+attemptName, withDelay=False, yrangeData=yrangeData, yrangeRain=yrangeRain)
                elif(testFroudeCatchment.subBasinDict[element].name == "BV Barrage Vesdre"):
                    stationName = "BV B Vesdre"
                    Qnat = naturalCatchment.subBasinDict[11].myHydro[:]

                    addData = []
                    addData.append(QVesdreFroude[:-1])
                    addData.append(QVesdreBeforeFroude[:-1])
                    addData.append(RV.MeasuresBVesIn.myHydro[:])

                    dtAddData = [testFroudeCatchment.deltaT,testFroudeCatchment.deltaT,RV.MeasuresBVesIn.deltaT]
                    beginDatesAddData = [testFroudeCatchment.dateBegin, testFroudeCatchment.dateBegin,RV.MeasuresBVesIn.dateBegin]
                    endDatesAddData = [testFroudeCatchment.dateEnd,testFroudeCatchment.dateEnd,RV.MeasuresBVesIn.dateEnd]
                    label_addData = ["Debits simulés avec apport de la Helle et de la Soor","BV avant modification du Froude", "Hydrogramme entrant reconstruit"]
                    color_addData = ["b","y","k"]

                    testFroudeCatchment.subBasinDict[element].plot_outlet(withEvap=False,rangeData=x_range,graph_title=stationName ,writeFile=writeDir+stationName+attemptName, withDelay=False, \
                        addData=addData,dt_addData=dtAddData,beginDates_addData=beginDatesAddData,endDates_addData=endDatesAddData,label_addData=label_addData,color_addData=color_addData)



    def outlet_all_basins_same_topo(self, plotDict={}, show=True):
        if(not("Time Zone Plot" in plotDict["General Parameters"])):
            tzPlot = 0
            tzDelta = datetime.timedelta(hours=0)
        else:
            tzPlot = plotDict["General Parameters"]["Time Zone Plot"]
            tzDelta = datetime.timedelta(hours=tzPlot)
        if(not("Date Begin" in plotDict["General Parameters"])):
            beginDate = []
            for idCatch in self.myCatchments:
                beginDate.append(self.myCatchments[idCatch]['Object'].dateBegin+tzDelta)
        else:
            beginDate = plotDict["General Parameters"]["Date Begin"]+tzDelta
            
        if(not("Date End" in plotDict["General Parameters"])):
            endDate = []
            for idCatch in self.myCatchments:
                endDate.append(self.myCatchments[idCatch]['Object'].dateEnd+tzDelta)
        else:
            endDate = plotDict["General Parameters"]["Date End"]+tzDelta
                
        if(not("Dt" in plotDict["General Parameters"])):
            dt=[]
            for idCatch in self.myCatchments:
                dt.append(self.myCatchments[idCatch]['Object'].deltaT)
        else:
            dt = plotDict["General Parameters"]["Dt"]


        basinId = [] # contains all the names of the subbasin
        basinNames = {}
        for idCatch in self.myCatchments:
            curCatch = self.myCatchments[idCatch]['Object']
            for id in curCatch.subBasinDict:
                curBasin = curCatch.subBasinDict[id]
                if(not(id in basinId) and (curBasin.name in plotDict)):
                    basinId.append(id)
                    basinNames[id] = (curBasin.name)



        nbCatchment = len(self.myCatchments)
        x_title = "Dates " + "(GMT+"+ str(tzPlot) + ")"


        if(not("Catchment colors" in plotDict["General Parameters"])):
            tmpColors = np.random.rand(nbCatchment)
            catchColors = []
            for icolor in range(len(tmpColors)):
                catchColors.append(tmpColors[icolor])
        else:
            catchColors = []
            catchColors = plotDict["General Parameters"]["Catchment colors"]
        if(len(catchColors)!=nbCatchment):
            print("ERROR: the number of catchments is not the same as the number of colors given")
            sys.exit()

        if("Same rain" in plotDict["General Parameters"]):
            sameRain = plotDict["General Parameters"]["Same rain"]
        else:
            sameRain = True

        if("Display rain" in plotDict["General Parameters"]):
            displayRain = plotDict["General Parameters"]["Display rain"]
        else:
            displayRain = True


        for id in basinId:
            
            y1 = []
            yLabels = []
            myTraits = []
            rain = []
            z = []
            nbAddRain=0
            y_labelAddRain = []
            upperPlot = False
            if(basinNames[id]=="BV Barrage Vesdre"):
                for idCatch in self.myCatchments:
                    curCatch = self.myCatchments[idCatch]['Object']
                    if(curCatch.myModel==cst.tom_UH):
                        tmp = curCatch.subBasinDict[18].myHydro[:] + curCatch.retentionBasinDict["J20"].get_outFlow_noDelay()
                        y1.append(tmp[:])
                    elif(curCatch.myModel==cst.tom_2layers_linIF):
                        tmp = np.sum(curCatch.subBasinDict[18].myHydro[:],1) + curCatch.retentionBasinDict["J20"].get_outFlow_noDelay()
                        y1.append(tmp[:])
                    yLabels.append(curCatch.name)
                    
                    if("Station Name" in plotDict[basinNames[id]]):
                        graph_title = plotDict[basinNames[id]]["Station Name"]
                    else:
                        graph_title = curCatch.subBasinDict[id].name
                    myTraits.append('-')
            elif(basinNames[id]=="BV Barrage Gileppe"):
                for idCatch in self.myCatchments:
                    curCatch = self.myCatchments[idCatch]['Object']
                    if(curCatch.myModel==cst.tom_UH):
                        tmp = curCatch.subBasinDict[19].myHydro[:] + curCatch.retentionBasinDict["J19"].get_outFlow_noDelay()
                        y1.append(tmp[:])
                    elif(curCatch.myModel==cst.tom_2layers_linIF):
                        tmp = np.sum(curCatch.subBasinDict[19].myHydro[:],1) + curCatch.retentionBasinDict["J19"].get_outFlow_noDelay()
                        y1.append(tmp[:])
                    yLabels.append(curCatch.name)
                    
                    if("Station Name" in plotDict[basinNames[id]]):
                        graph_title = plotDict[basinNames[id]]["Station Name"]
                    else:
                        graph_title = curCatch.subBasinDict[id].name
                    myTraits.append('-')
            else:
                for idCatch in self.myCatchments:
                    curCatch = self.myCatchments[idCatch]['Object']
                    tmp = curCatch.subBasinDict[id].get_outFlow_noDelay()
                    y1.append(tmp[:])
                    yLabels.append(curCatch.name)
                    
                    if("Station Name" in plotDict[basinNames[id]]):
                        graph_title = plotDict[basinNames[id]]["Station Name"]
                    else:
                        graph_title = curCatch.subBasinDict[id].name
                    myTraits.append('-')

                    if(sameRain and displayRain):
                        if(rain==[]):
                            rain = curCatch.subBasinDict[id].rain/curCatch.subBasinDict[id].surfaceDrainedHydro*3.6
                    elif(displayRain):
                        upperPlot = True
                        nbAddRain += 1
                        z.append(curCatch.subBasinDict[id].rain/curCatch.subBasinDict[id].surfaceDrainedHydro*3.6)
                        y_labelAddRain.append(curCatch.name)



            nbAddData = 0
            beginDateAddData = []
            endDateAddData = []
            dtAddData = []
            catchColorsAddData = []
            if("Add Data" in plotDict[basinNames[id]]):
                nbAddData = len(plotDict[basinNames[id]]["Add Data"]["Data"])
                for i in range(nbAddData):
                    y1.append(plotDict[basinNames[id]]["Add Data"]["Data"][i][:])
                    if("Date Begin" in plotDict[basinNames[id]]["Add Data"]):
                        beginDateAddData.append(plotDict[basinNames[id]]["Add Data"]["Date Begin"][i]+tzDelta)    
                    elif("Date Begin" in plotDict["General Parameters"]["Add Data"]):
                        beginDateAddData.append(plotDict["General Parameters"]["Add Data"]["Date Begin"][i]+tzDelta)

                    if("Date End" in plotDict[basinNames[id]]["Add Data"]):
                        endDateAddData.append(plotDict[basinNames[id]]["Add Data"]["Date End"][i]+tzDelta)    
                    elif("Date End" in plotDict["General Parameters"]["Add Data"]):
                        endDateAddData.append(plotDict["General Parameters"]["Add Data"]["Date End"][i]+tzDelta)

                    if("Dt" in plotDict[basinNames[id]]["Add Data"]):
                        dtAddData.append(plotDict[basinNames[id]]["Add Data"]["Dt"][i])    
                    elif("Dt" in plotDict["General Parameters"]["Add Data"]):
                        dtAddData.append(plotDict["General Parameters"]["Add Data"]["Dt"][i])

                    if("Labels" in plotDict[basinNames[id]]["Add Data"]):
                        yLabels.append(plotDict[basinNames[id]]["Add Data"]["Labels"][i])    
                    elif("Labels" in plotDict["General Parameters"]["Add Data"]):
                        yLabels.append(plotDict["General Parameters"]["Add Data"]["Labels"][i])

                    if("Colors" in plotDict[basinNames[id]]["Add Data"]):
                        catchColorsAddData.append(plotDict[basinNames[id]]["Add Data"]["Colors"][i])    
                    elif("Colors" in plotDict["General Parameters"]["Add Data"]):
                        catchColorsAddData.append(plotDict["General Parameters"]["Add Data"]["Colors"][i])

                    if("Type of Traits" in plotDict[basinNames[id]]["Add Data"]):
                        myTraits.append(plotDict[basinNames[id]]["Add Data"]["Type of Traits"][i])    
                    elif("Type of Traits" in plotDict["General Parameters"]["Add Data"]):
                        myTraits.append(plotDict["General Parameters"]["Add Data"]["Type of Traits"][i])

            if("Measures" in plotDict[basinNames[id]]):
                Measures = plotDict[basinNames[id]]["Measures"]
                myMeasure = Measures.myHydro
                yLabels.append("Mesures")
                catchColorsAddData.append('k')
                myTraits.append('-')
            else:
                myMeasure = []
                Measures = None
            
            if("X Range" in plotDict["General Parameters"]):
                xRange = plotDict["General Parameters"]["X Range"]
            else:
                xRange = []
            
            if("Y Range" in plotDict["General Parameters"]):
                yRange = plotDict["General Parameters"]["Y Range"]
            else:
                yRange = []

            if("Writing Directory" in plotDict["General Parameters"]):
                writeFile = plotDict["General Parameters"]["Writing Directory"]
            else:
                writeFile = ""





            # Plot Rains
            yTitles = "Débits [m³/s]"
            writeFileDef = writeFile + "OutFlow_" + graph_title.replace(".","")
            if(Measures!=None):
                ph.plot_hydro(nbCatchment+nbAddData,y1,rain=rain,x_title=x_title, y_titles=yTitles, beginDate=beginDate+beginDateAddData,endDate=endDate+endDateAddData,dt=dt+dtAddData,graph_title=graph_title, \
                            y_labels=yLabels,rangeData=xRange,y_data_range=yRange,myColors=catchColors+catchColorsAddData,typeOfTraits=myTraits,writeFile=writeFileDef,\
                            measures=myMeasure,beginDateMeasure=Measures.dateBegin+tzDelta, endDateMeasure=Measures.dateEnd+tzDelta, dtMeasure=Measures.deltaT,\
                            upperPlot=upperPlot,nbAddPlot=nbAddRain,z=z,y_labelAddPlot=y_labelAddRain)
            else:
                ph.plot_hydro(nbCatchment+nbAddData,y1,rain=rain,x_title=x_title, y_titles=yTitles, beginDate=beginDate+beginDateAddData,endDate=endDate+endDateAddData,dt=dt+dtAddData,graph_title=graph_title, \
                            y_labels=yLabels,rangeData=xRange,y_data_range=yRange,myColors=catchColors+catchColorsAddData,typeOfTraits=myTraits,writeFile=writeFileDef,\
                            upperPlot=upperPlot,nbAddPlot=nbAddRain,z=z,y_labelAddPlot=y_labelAddRain)

        if(show):
            plt.show()


        
    def outlet_all_RB_height_same_topo(self, plotDict={}, show=True):
        '''
        Plot the heights of all rentention basin. The measures given should also be heights in [m].
        This function considers that the topology in all the catchments is the same.
        '''
        if(not("Time Zone Plot" in plotDict["General Parameters"])):
            tzPlot = 0
            tzDelta = datetime.timedelta(hours=0)
        else:
            tzPlot = plotDict["General Parameters"]["Time Zone Plot"]
            tzDelta = datetime.timedelta(hours=tzPlot)
            
        if(not("Date Begin" in plotDict["General Parameters"])):
            beginDate = []
            for idCatch in self.myCatchments:
                beginDate.append(self.myCatchments[idCatch]['Object'].dateBegin+tzDelta)
        else:
            beginDate = plotDict["General Parameters"]["Date Begin"]+tzDelta
            
        if(not("Date End" in plotDict["General Parameters"])):
            endDate = []
            for idCatch in self.myCatchments:
                endDate.append(self.myCatchments[idCatch]['Object'].dateEnd+tzDelta)
        else:
            endDate = plotDict["General Parameters"]["Date End"]+tzDelta
                
        if(not("Dt" in plotDict["General Parameters"])):
            dt=[]
            for idCatch in self.myCatchments:
                dt.append(self.myCatchments[idCatch]['Object'].deltaT)
        else:
            dt = plotDict["General Parameters"]["Dt"]


        RBId = [] # contains all the names of the subbasin
        RBNames = {}
        for idCatch in self.myCatchments:
            curCatch = self.myCatchments[idCatch]['Object']
            for id in curCatch.retentionBasinDict:
                curBasin = curCatch.retentionBasinDict[id]
                if(not(id in RBId) and (curBasin.name in plotDict)):
                    RBId.append(id)
                    RBNames[id] = (curBasin.name)



        nbCatchment = len(self.myCatchments)
        x_title = "Dates " + "(GMT+" + str(tzPlot) + ")"


        if(not("Catchment colors" in plotDict["General Parameters"])):
            tmpColors = np.random.rand(nbCatchment)
            catchColors = []
            for icolor in range(len(tmpColors)):
                catchColors.append(tmpColors[icolor])
        else:
            catchColors = []
            catchColors = plotDict["General Parameters"]["Catchment colors"]
        if(len(catchColors)!=nbCatchment):
            print("ERROR: the number of catchments is not the same as the number of colors given")
            sys.exit()


        for id in RBId:
            
            y1 = []
            yLabels = []
            myTraits = []
            timeDelay = []
            for idCatch in self.myCatchments:
                curCatch = self.myCatchments[idCatch]['Object']
                myH = np.zeros(len(curCatch.retentionBasinDict[id].filledVolume))
                for ii in range(len(curCatch.retentionBasinDict[id].filledVolume)):
                    myH[ii] =  curCatch.retentionBasinDict[id].volume_to_h(curCatch.retentionBasinDict[id].filledVolume[ii])
                y1.append(myH[:])
                yLabels.append(curCatch.name)
                timeDelay.append(datetime.timedelta(seconds=curCatch.retentionBasinDict[id].timeDelay))

            beginDateRB = []
            endDateRB = []
            for ii in range(nbCatchment):
                beginDateRB.append(beginDate[ii] - timeDelay[ii])   # A ameliorer!!!
                endDateRB.append(endDate[ii] - timeDelay[ii])

                
                if("Station Name" in plotDict[RBNames[id]]):
                    graph_title = plotDict[RBNames[id]]["Station Name"]
                else:
                    graph_title = curCatch.retentionBasinDict[id].name
                myTraits.append('-')


            nbAddData = 0
            beginDateAddData = []
            endDateAddData = []
            dtAddData = []
            catchColorsAddData = []
            if("Add Data" in plotDict[RBNames[id]]):
                nbAddData = len(plotDict[RBNames[id]]["Add Data"])
                for i in range(nbAddData):
                    y1.append(plotDict[RBNames[id]]["Add Data"]["Data"][i][:])
                    if("Date Begin" in plotDict[RBNames[id]]["Add Data"]):
                        beginDateAddData.append(plotDict[RBNames[id]]["Add Data"]["Date Begin"][i]+tzDelta)    
                    elif("Date Begin" in plotDict["General Parameters"]["Add Data"]):
                        beginDateAddData.append(plotDict["General Parameters"]["Add Data"]["Date Begin"][i]+tzDelta)

                    if("Date End" in plotDict[RBNames[id]]["Add Data"]):
                        endDateAddData.append(plotDict[RBNames[id]]["Add Data"]["Date End"][i]+tzDelta)    
                    elif("Date End" in plotDict["General Parameters"]["Add Data"]):
                        endDateAddData.append(plotDict["General Parameters"]["Add Data"]["Date End"][i]+tzDelta)

                    if("Dt" in plotDict[RBNames[id]]["Add Data"]):
                        dtAddData.append(plotDict[RBNames[id]]["Add Data"]["Dt"][i])    
                    elif("Dt" in plotDict["General Parameters"]["Add Data"]):
                        dtAddData.append(plotDict["General Parameters"]["Add Data"]["Dt"][i])

                    if("Labels" in plotDict[RBNames[id]]["Add Data"]):
                        yLabels.append(plotDict[RBNames[id]]["Add Data"]["Labels"][i])    
                    elif("Labels" in plotDict["General Parameters"]["Add Data"]):
                        yLabels.append(plotDict["General Parameters"]["Add Data"]["Labels"][i])

                    if("Colors" in plotDict[RBNames[id]]["Add Data"]):
                        catchColorsAddData.append(plotDict[RBNames[id]]["Add Data"]["Colors"][i])    
                    elif("Colors" in plotDict["General Parameters"]["Add Data"]):
                        catchColorsAddData.append(plotDict["General Parameters"]["Add Data"]["Colors"][i])

                    if("Type of Traits" in plotDict[RBNames[id]]["Add Data"]):
                        myTraits.append(plotDict[RBNames[id]]["Add Data"]["Type of Traits"][i])    
                    elif("Type of Traits" in plotDict["General Parameters"]["Add Data"]):
                        myTraits.append(plotDict["General Parameters"]["Add Data"]["Type of Traits"][i])

            if("Y Range" in plotDict[RBNames[id]]):
                yRange = plotDict[RBNames[id]]["Y Range"]
            elif("Y Range" in plotDict["General Parameters"]):
                yRange = plotDict["General Parameters"]["Y Range"]
            else:
                yRange = []

            if("Measures" in plotDict[RBNames[id]]):
                Measures = plotDict[RBNames[id]]["Measures"]
                myMeasure = Measures.myHydro
                yLabels.append("Mesures")
                catchColorsAddData.append('k')
                myTraits.append('--')
            else:
                myMeasure = []
                Measures = None
            
            if("X Range" in plotDict["General Parameters"]):
                xRange = plotDict["General Parameters"]["X Range"]
            else:
                xRange = []
            

            if("Writing Directory" in plotDict["General Parameters"]):
                writeFile = plotDict["General Parameters"]["Writing Directory"]
            else:
                writeFile = ""





            # Plot Rains
            yTitles = "Hauteurs d'eau [m]"
            writeFileDef = writeFile + "_H_" + graph_title.replace(".","")
            if(Measures!=None):
                ph.plot_hydro(nbCatchment+nbAddData, y1,x_title=x_title, y_titles=yTitles, beginDate=beginDateRB+beginDateAddData,endDate=endDateRB+endDateAddData,dt=dt+dtAddData,graph_title=graph_title, \
                            y_labels=yLabels,rangeData=xRange,y_data_range=yRange,myColors=catchColors+catchColorsAddData,typeOfTraits=myTraits,writeFile=writeFileDef,\
                            measures=myMeasure,beginDateMeasure=Measures.dateBegin+tzDelta, endDateMeasure=Measures.dateEnd+tzDelta, dtMeasure=Measures.deltaT)
            else:
                ph.plot_hydro(nbCatchment+nbAddData, y1,x_title=x_title, y_titles=yTitles, beginDate=beginDate+beginDateAddData,endDate=endDate+endDateAddData,dt=dt+dtAddData,graph_title=graph_title, \
                            y_labels=yLabels,rangeData=xRange,y_data_range=yRange,myColors=catchColors+catchColorsAddData,typeOfTraits=myTraits,writeFile=writeFileDef)

        if(show):
            plt.show()

    