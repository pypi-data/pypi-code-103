# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 23:07:00 2021

@author: nkdi
"""
import numpy as np
def TrigonometricToAzimuth(Theta,AzimuthToTrigonometric = None,Rad = None):

    if AzimuthToTrigonometric is None:
        AzimuthToTrigonometric = 0

    if Rad is None:
        Rad = 0

    if Rad == 1:
        ThetaDiff = np.pi/2
        ThetaMax = 2*np.pi
        ThetaMin = 0
    else:
        ThetaDiff = 90
        ThetaMax = 360
        ThetaMin = 0

    if AzimuthToTrigonometric == 0:
        ThetaOut = -np.asarray(Theta) + ThetaDiff
    elif AzimuthToTrigonometric == 1:
        ThetaOut = ThetaDiff - np.asarray(Theta)
        
    ThetaOut = np.asarray(ThetaOut) # Avoid problems when evaluating scalars

    ThetaOut[ThetaOut < ThetaMin] = ThetaOut[ThetaOut < ThetaMin] + ThetaMax
    ThetaOut[ThetaOut >= ThetaMax] = ThetaOut[ThetaOut >= ThetaMax] - ThetaMax

    return ThetaOut

def FarmUpwindDisturbances(ThetaRange,TurbineIDs,TurbinePosLon,TurbinePosLat,OutputTurbineIDs=None,ThetaRelRange=None):

    if OutputTurbineIDs is None:
        OutputTurbineIDs = TurbineIDs
    if ThetaRelRange is None:
        ThetaRelRange = 16
    TurbineIDsNumeric = np.atleast_2d(np.arange(len(TurbineIDs))).T

    DX = np.dot(np.atleast_2d(TurbinePosLon).T,np.ones((1,len(TurbinePosLon)))) - np.dot(np.ones((len(TurbinePosLon),1)),np.atleast_2d(TurbinePosLon))
    DY = np.dot(np.atleast_2d(TurbinePosLat).T,np.ones((1,len(TurbinePosLat)))) - np.dot(np.ones((len(TurbinePosLat),1)),np.atleast_2d(TurbinePosLat))

    Theta = np.arctan2(DY,DX)
    Theta = Theta + (Theta < 0)*2*np.pi
    Theta = Theta - (Theta > 2*np.pi)*2*np.pi
    ThetaDeg = Theta*180/np.pi
    Rdist = np.sqrt(DX**2 + DY**2)

    NOutputTurbines = len(OutputTurbineIDs)
    ClosestDisturbanceID = np.zeros((len(ThetaRange),NOutputTurbines))
    ClosestDisturbanceDist = np.zeros((len(ThetaRange),NOutputTurbines))
    ClosestDisturbanceRelAngle = np.zeros((len(ThetaRange),NOutputTurbines))


    DisturbanceList = [[] for _ in range(len(ThetaRange))]
    DisturbanceDist = [[] for _ in range(len(ThetaRange))]
    DisturbanceAzimuth = [[] for _ in range(len(ThetaRange))]
    DisturbanceRelAngle = [[] for _ in range(len(ThetaRange))]
    ClosestDisturbanceID = [[] for _ in range(len(ThetaRange))]
    ClosestDisturbanceDist = np.zeros((len(ThetaRange),len(OutputTurbineIDs)))
    ClosestDisturbanceRelAngle = np.zeros((len(ThetaRange),len(OutputTurbineIDs)))

    for iT in range(len(ThetaRange)):
        Thetai = TrigonometricToAzimuth(ThetaRange[iT],1,0) # Azimuth to trigonometric in degrees    
        DisturbanceList[iT] = [[] for _ in range(len(OutputTurbineIDs))]
        DisturbanceDist[iT] = [[] for _ in range(len(OutputTurbineIDs))]
        DisturbanceAzimuth[iT] = [[] for _ in range(len(OutputTurbineIDs))]
        DisturbanceRelAngle[iT] = [[] for _ in range(len(OutputTurbineIDs))]
        ClosestDisturbanceID[iT] = [[] for _ in range(len(OutputTurbineIDs))]
        for iO in range(len(OutputTurbineIDs)):
            CurrentTurbine = np.argwhere(OutputTurbineIDs[iO]==TurbineIDs)[0]
            ThetaC = ThetaDeg[:,CurrentTurbine]
            RdistC = Rdist[:,CurrentTurbine]
            Rindex = RdistC>0
            ThetaDegW = ThetaC[Rindex == True]
            RdistW = RdistC[Rindex==True]
            TurbineIDsW = TurbineIDsNumeric[Rindex==True]    
            Tindex = ((ThetaDegW >= (Thetai - ThetaRelRange)) & (ThetaDegW < (Thetai + ThetaRelRange))) | ((ThetaDegW > (Thetai - ThetaRelRange + 360)) | (ThetaDegW < (Thetai + ThetaRelRange - 360)))
            if sum(Tindex==True) > 0:
                ThetaDegSector = ThetaDegW[Tindex]
                RdistSector = RdistW[Tindex]
                TurbineIDsSector = TurbineIDsW[Tindex]
                DistanceSortIndex = np.argsort(RdistSector)
                iDistancesSort = RdistSector[DistanceSortIndex]
                DisturbanceList[iT][iO] = TurbineIDs[TurbineIDsSector[DistanceSortIndex]]
                DisturbanceDist[iT][iO] = iDistancesSort
                DisturbanceAzimuth[iT][iO] = TrigonometricToAzimuth(ThetaDegSector[DistanceSortIndex])
                RelativeAnglei = ThetaRange[iT] - TrigonometricToAzimuth(ThetaDegSector[DistanceSortIndex])
                RelativeAnglei = RelativeAnglei - (RelativeAnglei > 180)*360
                RelativeAnglei = RelativeAnglei + (RelativeAnglei < -180)*360
                DisturbanceRelAngle[iT][iO] = RelativeAnglei                        
                ClosestDisturbanceID[iT][iO] = TurbineIDs[TurbineIDsSector[DistanceSortIndex[0]]]
                ClosestDisturbanceDist[iT,iO] = iDistancesSort[0]
                ClosestDisturbanceRelAngle[iT,iO] = RelativeAnglei[0]
    
    return DisturbanceList,DisturbanceDist,DisturbanceRelAngle,DisturbanceAzimuth,ClosestDisturbanceID,ClosestDisturbanceDist,ClosestDisturbanceRelAngle

def CircularMean_D(x):
    import numpy as np
    x = np.asarray(x[~np.isnan(np.asarray(x,dtype = 'float64'))],dtype = 'float64')
    mu = np.arctan2(np.mean(np.sin(x*np.pi/180)),np.mean(np.cos(x*np.pi/180)))*180/np.pi
    mu+=360*((mu<=-0.5)==True)
    return mu

def EncodeWindFarmGeometry(TurbinePosLon,TurbinePosLat,ThetaRange, method = None, inputs = None):
    from hipersim.surrogates.farm_utils import FarmUpwindDisturbances
    if method is None:
        method = 'RelativeLocation'


    Nturbines = len(TurbinePosLon)
    Nthetas = len(ThetaRange)
    TurbineIDNumeric = np.arange(1,Nturbines+1)        
    
    if method == 'RelativeLocation':
        if inputs is None:
            inputs = dict()
        if 'Nclosest' not in inputs:
            inputs['Nclosest'] = 10        
        Nclosest = inputs['Nclosest']
        DisturbanceList,DisturbanceDist,DisturbanceRelAngle,__,__,__,__ = FarmUpwindDisturbances(ThetaRange,TurbineIDNumeric,TurbinePosLon,TurbinePosLat,None,None)    
        X = np.zeros((Nturbines*Nthetas,Nclosest*2))
        for iTheta in range(Nthetas):
            for iTurb in range(Nturbines):
                nDisturb = len(DisturbanceList[iTheta][iTurb])
                nDisturb = np.min((nDisturb,Nclosest))
                X[iTheta*Nturbines + iTurb,:nDisturb] = DisturbanceDist[iTheta][iTurb][:nDisturb]
                X[iTheta*Nturbines + iTurb,Nclosest:(Nclosest + nDisturb)] = np.sin(np.deg2rad(DisturbanceRelAngle[iTheta][iTurb][:nDisturb]))*DisturbanceDist[iTheta][iTurb][:nDisturb]
    
    if method == 'Autoencoder':
        from hipersim.surrogates.os_utils import load_packaged_model
        if inputs is None:
            inputs = dict()
        if 'Modelfile' not in inputs:
            inputs['Modelfile'] = 'AutoencoderModel_v0.sav'            
        if 'Nclosest' not in inputs:
            inputs['Nclosest'] = 20            
        Nclosest = inputs['Nclosest']
        DisturbanceList,DisturbanceDist,DisturbanceRelAngle,__,__,__,__ = FarmUpwindDisturbances(ThetaRange,TurbineIDNumeric,TurbinePosLon,TurbinePosLat,None,None)    
        X = np.zeros((Nturbines*Nthetas,Nclosest*2))
        for iTheta in range(Nthetas):
            for iTurb in range(Nturbines):
                nDisturb = len(DisturbanceList[iTheta][iTurb])
                nDisturb = np.min((nDisturb,Nclosest))
                X[iTheta*Nturbines + iTurb,:nDisturb] = DisturbanceDist[iTheta][iTurb][:nDisturb]
                X[iTheta*Nturbines + iTurb,Nclosest:(Nclosest + nDisturb)] = np.sin(np.deg2rad(DisturbanceRelAngle[iTheta][iTurb][:nDisturb]))*DisturbanceDist[iTheta][iTurb][:nDisturb]
        
        ANN = load_packaged_model(inputs['Modelfile'])
        X = ANN.predict(X)
    
    return X