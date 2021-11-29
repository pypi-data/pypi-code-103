'''
 http://www.ce.utexas.edu/prof/Novoselac/classes/ARE383/Handouts/F01_06SI.pdf
Nomenclature
 Tdb = dry bulb temperature in Celcius
 Twb = wet bulb temperature in Celcius
 Tdp = dew point temperature in Celcius
 w = moisture content (kg H20 / kg dry air)
 h enthalpy J/kg*K
 RH relative humidity
 P pressure in Pa
'''
import numpy as np
import copy

def psychometric(val,prop):
    if prop in val:
        del val[prop]
    kys = list(val.keys())
    try:
        n = len(val[kys[0]])
        air = copy.deepcopy(val)
        single = False
    except TypeError:
        air = {}
        for i in kys:
            air[i] = [copy.deepcopy(val[i])]
        single = True
        n=1
    if 'P' not in air:
        air['P'] = [101325 for i in range(n)]# atmospheric pressure (Pa)
        # air['P'] = 101325*(1-2.25577e-5*z)**5.2559 # atmospheric pressure function of height z(Pa)
        # air['Tdb'] = 15-0.0065*z # atmospheric  temperature function of height z(C)
    if 'h' in air and 'w' in air:
        air['Tdb'] = [(air['h'][i]/1000 - air['w'][i]*2501)/(1.006 + air['w'][i]*1.86) for i in range(n)] #Temperature in C and converting enthalpy to kJ/kg and humidity in massH2O/massAir
    elif 'h' in air and 'Tdb' in air:
        air['w'] = [(air['h'][i]/1000 - 1.006*air['Tdb'][i])/(2501 + 1.86*air['Tdb'][i]) for i in range(n)] #kJ/kg 
    elif 'RH' in air and 'Tdb' in air:
        satP = sat_press(air['Tdb'])
        P_H2O = [air['RH'][i]/100*satP[i]  for i in range(n)] #kPa
        air['w'] = [.621945*(P_H2O[i]/(air['P'][i]-P_H2O[i])) for i in range(n)]
    elif 'Twb' in air and 'w' in air:
        satP = sat_press(air['Twb']) #very small error introduced using the wet_bulb temperature for saturation pressure
        W_s = [0.62198*satP[i]/(air['P'][i]-satP[i]) for i in range(n)]
        air['Tdb'] = [(air['Twb'][i]*(4.186*air['w'][i]-2.381*W_s[i] + 1.006) +2501*W_s[i] - air['w'][i]*2501)/(1.805*air['w'][i]+1.006) for i in range(n)]
    elif 'Twb' in air:
        # assumes saturated
        air['Tdb'] = copy.deepcopy(air['Twb'])
        satP = sat_press(air['Tdb'])
        air['w'] = [0.62198*satP[i]/(air['P'][i]-satP[i]) for i in range(n)]
    elif 'Tdp' in air:
        # assumes saturated
        air['Tdb'] = copy.deepcopy(air['Tdp'])
        satP = sat_press(air['Tdp'])
        air['w'] = [0.62198*satP[i]/(air['P'][i]-satP[i]) for i in range(n)]
    elif 'h' in air:
        # assumes saturated
        air['Tdb'] = [10 for i in range(n)]
        for i in range(5):
            satP = sat_press(air['Tdb'])
            air['w'] = [0.62198*satP[i]/(air['P'][i]-satP[i]) for i in range(n)]
            air['Tdb'] = [0.7*air['Tdb'][i]  + 0.3*(air['h'][i]/1000 - air['w'][i]*2501)/(1.006 + air['w'][i]*1.86) for i in range(n)]
    
    
    if prop =='h':
            air['h'] = [1000*(1.006*air['Tdb'][i] + air['w'][i]*(2501 + 1.86*air['Tdb'][i])) for i in range(n)]
    elif prop =='Twb':
            #not perfect but close (0.26C) % https://journals.ametsoc.org/doi/full/10.1175/JAMC-D-11-0143.1
            satP = sat_press(air['Tdb'])
            P_H2O = [air['P'][i]*air['w'][i]/(0.62198 + air['w'][i]) for i in range(n)]
            air['RH'] = [P_H2O[i]/satP[i]*100  for i in range(n)] #Relative humidity in percent
            air['Twb'] = [float(air['Tdb'][i]*np.arctan(0.151977*(air['RH'][i] + 8.313659)**.5) + np.arctan(air['Tdb'][i] + air['RH'][i]) - np.arctan(air['RH'][i] - 1.676331) + 0.00391838*(air['RH'][i])**(3/2)*np.arctan(0.023101*air['RH'][i]) - 4.686035)  for i in range(n)]
    elif prop =='Tdp':
            air['Tdp'] = dew_point(air['Tdb'],air['P'],air['w'])
    elif prop =='RH':
            satP = sat_press(air['Tdb'])
            P_H2O = [air['P'][i]*air['w'][i]/(0.62198 + air['w'][i]) for i in range(n)]
            air['RH'] = [P_H2O[i]/satP[i]*100 for i in range(n)] #Relative humidity in percent
    elif prop =='T':
            air['T'] = copy.deepcopy(air['Tdb'])
    if single:
        kys = list(air.keys())
        for i in kys:
            air[i] = copy.deepcopy(air[i][0])
    out = copy.deepcopy(air[prop])
    return out

def dew_point(T,P,w):
    n = len(T)
    P_H2O = [P[i]*w[i]/(0.62198 + w[i])/1000 for i in range(n)] # kPa 0.62198 is ratio of molar masses
    Tdp = [[] for i in range(n)]
    for i in range(n):
        if T[i]<0:
            Tdp[i] = float(6.09 + 12.608*np.log(P_H2O[i]) + 0.4959*np.log(P_H2O[i])**2)
        else:
            Tdp[i] = float(6.54 + 14.526*np.log(P_H2O[i]) + 0.7389*np.log(P_H2O[i])**2 + 0.09486*np.log(P_H2O[i])**3 + 0.4569*(P_H2O[i])**0.1984) #Dew point from partial pressure of water using ASHRAE 2013 Fundamentals eqn 39 valid from 0C to 93C
    return Tdp

def sat_press(T):
    n = len(T)
    Tdb_K = [T[i]+273.15 for i in range(n)] #Tdb (Kelvin)
    satP = [[] for i in range(n)]
    for i in range(n):
        if T[i]<0:
            satP[i] = float(np.exp((-5.6745359e3)/Tdb_K[i] + 6.3925247 - 9.677843e-3*Tdb_K[i] + 6.22157e-7*Tdb_K[i]**2 + 2.0747825e-9*Tdb_K[i]**3 -9.484024e-13*Tdb_K[i]**4 + 4.1635019*np.log(Tdb_K[i]))) # Pa, saturated water vapor pressure ASHRAE 2013 fundamentals eq. 6 in kPa valid for 0 to 200C
        else:
            satP[i] = float(np.exp((-5.8002206e3)/Tdb_K[i] + 1.3914993 - 4.8640239e-2*Tdb_K[i] + 4.1764768e-5*Tdb_K[i]**2 - 1.4452093e-8*Tdb_K[i]**3 + 6.5459673*np.log(Tdb_K[i]))) # Pa saturated water vapor pressure ASHRAE 2013 fundamentals eq. 6 in kPa valid for 0 to 200C
    return satP